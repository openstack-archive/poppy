# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import random
import uuid

import ddt
import mock
from oslo_config import cfg
import requests

from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.taskflow.task import create_service_tasks
from poppy.distributed_task.taskflow.task import delete_service_tasks
from poppy.distributed_task.taskflow.task import purge_service_tasks
from poppy.distributed_task.taskflow.task import update_service_tasks
from poppy.distributed_task.utils import memoized_controllers
from poppy.manager.default import driver


from poppy.manager.default import services
from poppy.model import flavor
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import service
from tests.unit import base


class Elapsed(object):
    def __init__(self, time):
        self.time = time

    def total_seconds(self):
        return self.time


class Response(object):

    def __init__(self, resp_status, resp_json=None):
        self.resp_status = resp_status
        self.resp_json = resp_json

    def headers(self):
        return {}

    @property
    def ok(self):
        return self.resp_status

    def json(self):
        return self.resp_json

    @property
    def elapsed(self):
        return Elapsed(0.1)


class MonkeyPatchControllers(object):

    def __init__(self, service_controller,
                 dns_controller,
                 storage_controller, func):
        self.service_controller = service_controller
        self.dns_controller = dns_controller
        self.storage_controller = storage_controller
        self.func = func

    def __enter__(self):
        def monkey_task_controllers(program, controller=None):

            if controller == 'storage':
                return self.service_controller, self.storage_controller
            if controller == 'dns':
                return self.service_controller, self.dns_controller
            else:
                return self.service_controller

        memoized_controllers.task_controllers = monkey_task_controllers

    def __exit__(self, exc_type, exc_val, exc_tb):
        memoized_controllers.task_controllers = self.func


@ddt.ddt
class DefaultManagerServiceTests(base.TestCase):

    @mock.patch('poppy.bootstrap.Bootstrap')
    @mock.patch('poppy.notification.base.driver.NotificationDriverBase')
    @mock.patch('poppy.dns.base.driver.DNSDriverBase')
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.distributed_task.base.driver.DistributedTaskDriverBase')
    def setUp(self, mock_distributed_task, mock_storage,
              mock_dns, mock_notification, mock_bootstrap):
        # NOTE(TheSriram): the mock.patch decorator applies mocks
        # in the reverse order of the arguments present
        super(DefaultManagerServiceTests, self).setUp()

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        self.bootstrap_obj = mock_bootstrap(conf)

        # mock a stevedore provider extension
        def get_provider_by_name(name):
            name_p_name_mapping = {
                'maxcdn': 'MaxCDN',
                'cloudfront': 'CloudFront',
                'fastly': 'Fastly',
                'mock': 'Mock'
            }
            return mock.Mock(obj=mock.Mock(provider_name=(
                name_p_name_mapping[name])))
        mock_providers = mock.MagicMock()
        mock_providers.__getitem__.side_effect = get_provider_by_name
        manager_driver = driver.DefaultManagerDriver(conf,
                                                     mock_storage,
                                                     mock_providers,
                                                     mock_dns,
                                                     mock_distributed_task,
                                                     mock_notification)

        # stubbed driver
        self.sc = services.DefaultServicesController(manager_driver)
        self.bootstrap_obj.manager = manager_driver
        self.bootstrap_obj.manager.services_controller = self.sc
        self.project_id = str(uuid.uuid4())
        self.service_name = str(uuid.uuid4())
        self.service_id = str(uuid.uuid4())
        self.auth_token = str(uuid.uuid4())
        self.service_json = {
            "name": self.service_name,
            "domains": [
                {"domain": "www.mywebsite.com"},
                {"domain": "blog.mywebsite.com"},
            ],
            "origins": [
                {
                    "origin": "mywebsite.com",
                    "port": 80,
                    "ssl": False
                }
            ],
            "caching": [
                {"name": "default",
                 "ttl": 3600},
                {"name": "home",
                 "ttl": 17200,
                 "rules": [
                     {"name": "index", "request_url": "/index.htm"}
                 ]
                 },
                {"name": "images",
                 "ttl": 12800,
                 "rules": [
                     {"name": "pictures",
                      "request_url": "/pictures.htm"}
                 ]
                 }
            ],
            "flavor_id": "standard",
            "log_delivery": {
                "enabled": False
            },
        }

        self.service_obj = service.load_from_json(self.service_json)

    @mock.patch('poppy.bootstrap.Bootstrap')
    def mock_purge_service(self, mock_bootstrap):
        mock_bootstrap.return_value = self.bootstrap_obj
        purge_provider = purge_service_tasks.PurgeProviderServicesTask()
        provider_details = json.dumps(
            dict([(k, v.to_dict()) for k, v
                  in self.provider_details.items()]))
        responders = purge_provider.execute(provider_details, str(None))
        error_update = common.UpdateProviderDetailErrorTask()
        changed_provider_details_dict = error_update.execute(responders,
                                                             self.service_id,
                                                             provider_details)
        not_empty_update = common.UpdateProviderDetailIfNotEmptyTask()
        not_empty_update.execute(changed_provider_details_dict,
                                 self.project_id,
                                 self.service_id)

    @mock.patch('poppy.bootstrap.Bootstrap')
    def mock_delete_service(self, mock_bootstrap):
        mock_bootstrap.return_value = self.bootstrap_obj
        delete_provider = delete_service_tasks.DeleteProviderServicesTask()
        provider_details = json.dumps(
            dict([(k, v.to_dict()) for k, v
                  in self.provider_details.items()]))
        responders = delete_provider.execute(provider_details)
        delete_dns = delete_service_tasks.DeleteServiceDNSMappingTask()
        dns_responders = delete_dns.execute(provider_details, 0)

        gather_provider = delete_service_tasks.GatherProviderDetailsTask()
        changed_provider_dict = gather_provider.execute(responders,
                                                        dns_responders,
                                                        provider_details)
        update_provider = common.UpdateProviderDetailIfNotEmptyTask()
        update_provider.execute(changed_provider_dict, self.project_id,
                                self.service_id)

        delete_service = delete_service_tasks.DeleteStorageServiceTask()
        delete_service.execute(self.project_id, self.service_id)

    def mock_create_service(self, provider_details_json):
        @mock.patch('poppy.bootstrap.Bootstrap')
        def bootstrap_mock_create(mock_bootstrap):
            mock_bootstrap.return_value = self.bootstrap_obj

            create_provider = create_service_tasks.CreateProviderServicesTask()
            responders = create_provider.execute(
                json.dumps(provider_details_json),
                self.project_id,
                self.service_id)
            create_dns = create_service_tasks.CreateServiceDNSMappingTask()
            dns_responder = create_dns.execute(responders, 0)
            gather_provider = create_service_tasks.GatherProviderDetailsTask()
            log_responder = \
                create_service_tasks.CreateLogDeliveryContainerTask()
            provider_details_dict = \
                gather_provider.execute(responders,
                                        dns_responder,
                                        log_responder)
            update_provider_details = common.UpdateProviderDetailTask()
            update_provider_details.execute(provider_details_dict,
                                            self.project_id, self.service_id)

        bootstrap_mock_create()

    def mock_update_service(self, provider_details_json):
        @mock.patch('poppy.bootstrap.Bootstrap')
        def bootstrap_mock_update(mock_bootstrap):
            mock_bootstrap.return_value = self.bootstrap_obj
            service_old = json.dumps(self.service_json)
            update_provider = update_service_tasks.UpdateProviderServicesTask()
            service_updates = self.service_json.copy()
            service_updates['log_delivery'] = {
                'enabled': True
            }
            service_updates_json = json.dumps(service_updates)
            responders = update_provider.execute(
                service_old,
                service_updates_json
            )
            update_dns = update_service_tasks.UpdateServiceDNSMappingTask()

            dns_responder = update_dns.execute(responders, 0, service_old,
                                               service_updates_json)

            log_delivery_update = \
                update_service_tasks.UpdateLogDeliveryContainerTask()
            log_responder = log_delivery_update.execute(self.project_id,
                                                        self.auth_token,
                                                        service_old,
                                                        service_updates_json)

            gather_provider = update_service_tasks.GatherProviderDetailsTask()

            provider_details_dict = \
                gather_provider.execute(responders,
                                        dns_responder,
                                        log_responder,
                                        self.project_id,
                                        self.service_id,
                                        service_old)

            update_provider_details = \
                update_service_tasks.UpdateProviderDetailsTask_Errors()
            update_provider_details.execute(provider_details_dict,
                                            self.project_id,
                                            self.service_id,
                                            service_old,
                                            service_updates_json)

        bootstrap_mock_update()

    def test_create(self):
        # fake one return value
        self.sc.flavor_controller.get.return_value = flavor.Flavor(
            "standard",
            [flavor.Provider("cloudfront", "www.cloudfront.com"),
             flavor.Provider("fastly", "www.fastly.com"),
             flavor.Provider("mock", "www.mock_provider.com")]
        )

        providers = self.sc._driver.providers

        # mock responses from provider_wrapper.create call
        # to get code coverage
        def get_provider_extension_by_name(name):
            if name == "cloudfront":
                return_mock = mock.Mock(
                    return_value={
                        'Cloudfront': {
                            'id':
                            '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                            'links': [
                                {
                                    'href': 'www.mysite.com',
                                    'rel': 'access_url'}],
                            'status': "deploy_in_progress"}})
                service_controller = mock.Mock(
                    create=return_mock)
                return mock.Mock(obj=mock.Mock(
                    provider_name='CloudFront',
                    service_controller=service_controller)
                )
            elif name == "fastly":
                return_mock = mock.Mock(
                    return_value={
                        'Fastly': {'error': "fail to create service",
                                   'error_detail': 'Fastly Create failed'
                                   ' because of XYZ'}})

                service_controller = mock.Mock(
                    create=return_mock)
                return mock.Mock(obj=mock.Mock(
                    provider_name=name.title(),
                    service_controller=service_controller)
                )
            else:
                return_mock = mock.Mock(
                    return_value={
                        name.title(): {
                            'id':
                            '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                            'links': [
                                {
                                    'href': 'www.mysite.com',
                                    'rel': 'access_url'}]}})
                service_controller = mock.Mock(
                    create=return_mock)
                return mock.Mock(obj=mock.Mock(
                    provider_name=name.title(),
                    service_controller=service_controller)
                )

        providers.__getitem__.side_effect = get_provider_extension_by_name

        service_obj = self.sc.create(self.project_id,
                                     self.auth_token,
                                     self.service_json)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage_controller.create.assert_called_once_with(
            self.project_id,
            service_obj)

    @ddt.file_data('data_provider_details.json')
    def test_create_service_worker(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', None)
            status = provider_detail_dict.get('status', u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

            providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return_mock = {
                    'CloudFront': {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                        'links': [{'href': 'www.mysite.com',
                                   'rel': 'access_url'}],
                        'status': 'deploy_in_progress'
                    }
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='CloudFront',
                    service_controller=service_controller)
                )
            elif name == 'fastly':
                return_mock = {
                    'Fastly': {'error': "fail to create servcice",
                               'error_detail': 'Fastly Create failed'
                               '     because of XYZ'}
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='MaxCDN',
                    service_controller=service_controller)
                )
            else:
                return_mock = {
                    name.title(): {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                        'links': [
                            {'href': 'www.mysite.com',
                             'rel': 'access_url'}]
                    }
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name=name.title(),
                    service_controller=service_controller)
                )

        providers.__getitem__.side_effect = get_provider_extension_by_name

        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):
            self.mock_create_service(provider_details_json)

    @ddt.file_data('data_provider_details.json')
    def test_update_service_worker_success_and_failure(self,
                                                       provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', None)
            status = provider_detail_dict.get('status', u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

            providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return_mock = {
                    'CloudFront': {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                        'links': [{'href': 'www.mysite.com',
                                   'rel': 'access_url'}],
                        'status': 'deploy_in_progress'
                    }
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='CloudFront',
                    service_controller=service_controller)
                )
            elif name == 'fastly':
                return_mock = {
                    'Fastly': {'error': "fail to create servcice",
                               'error_detail': 'Fastly Create failed'
                               '     because of XYZ'}
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='MaxCDN',
                    service_controller=service_controller)
                )
            else:
                return_mock = {
                    name.title(): {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                        'links': [
                            {'href': 'www.mysite.com',
                             'rel': 'access_url'}]
                    }
                }
                service_controller = mock.Mock(
                    create=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name=name.title(),
                    service_controller=service_controller)
                )

        providers.__getitem__.side_effect = get_provider_extension_by_name

        conf = cfg.CONF
        conf(project='poppy', prog='poppy', args=[])
        LOG_DELIVERY_OPTIONS = [
            cfg.ListOpt('preferred_dcs', default=['DC1', 'DC2'],
                        help='Preferred DCs to create container'),
        ]

        LOG_DELIVERY_GROUP = 'log_delivery'
        conf.register_opts(LOG_DELIVERY_OPTIONS, group=LOG_DELIVERY_GROUP)
        region = random.choice(conf['log_delivery']['preferred_dcs'])

        catalog_json = {
            'access': {
                'serviceCatalog': [
                    {
                        'type': 'object-store',
                        'endpoints': [
                            {
                                'region': region,
                                'publicURL': 'public',
                                'internalURL': 'private'
                            }
                        ]
                    }
                    ]
                }
            }
        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):

            # NOTE(TheSriram): Successful update
            with mock.patch.object(requests,
                                   'post',
                                   return_value=Response(True, catalog_json)):
                with mock.patch.object(requests,
                                       'put',
                                       return_value=Response(True)):
                    self.mock_update_service(provider_details_json)

            # NOTE(TheSriram): Unsuccessful update due to keystone
            with mock.patch.object(requests,
                                   'post',
                                   return_value=Response(False, catalog_json)):
                with mock.patch.object(requests,
                                       'put',
                                       return_value=Response(True)):
                    self.mock_update_service(provider_details_json)

            # NOTE(TheSriram): Unsuccessful update due to swift
            with mock.patch.object(requests,
                                   'post',
                                   return_value=Response(True, catalog_json)):
                with mock.patch.object(requests,
                                       'put',
                                       return_value=Response(False)):
                    self.mock_update_service(provider_details_json)

    @ddt.file_data('service_update.json')
    def test_update(self, update_json):
        provider_details_dict = {
            "MaxCDN": {"id": 11942, "access_urls": ["mypullzone.netdata.com"]},
            "Mock": {"id": 73242, "access_urls": ["mycdn.mock.com"]},
            "CloudFront": {
                "id": "5ABC892", "access_urls": ["cf123.cloudcf.com"]},
            "Fastly": {
                "id": 3488, "access_urls": ["mockcf123.fastly.prod.com"]}
        }
        providers_details = {}
        for name in provider_details_dict:
            details = provider_details_dict[name]
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=details['id'],
                access_urls=details['access_urls'],
                status=details.get('status', u'unknown'))
            providers_details[name] = provider_detail_obj

        providers = self.sc._driver.providers

        self.sc.storage_controller.get_provider_details.return_value = (
            providers_details
        )

        service_obj = service.load_from_json(self.service_json)
        service_obj.status = u'deployed'
        self.sc.storage_controller.get.return_value = service_obj
        service_updates = json.dumps([
            {
                "op": "replace",
                "path": "/domains/0",
                "value": {"domain": "added.mocksite4.com"}
            }
        ])

        self.sc.update(self.project_id,
                       self.service_id,
                       self.auth_token,
                       service_updates)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage_controller.update.assert_called_once()

        # and that the providers are notified.
        providers.map.assert_called_once()

    @ddt.file_data('data_provider_details.json')
    def test_delete(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        self.service_obj.provider_details = self.provider_details
        sc = self.sc.storage_controller
        sc.get.return_value = self.service_obj

        self.sc.delete(self.project_id, self.service_id)

        # ensure the manager calls the storage driver with the appropriate data

        sc.get.assert_called_once_with(self.project_id, self.service_id)
        sc.update.assert_called_once_with(self.project_id,
                                          self.service_id,
                                          self.service_obj)

        # break into 2 lines.
        sc = self.sc.storage_controller
        sc.get_provider_details.assert_called_once_with(
            self.project_id,
            self.service_id)

    @ddt.file_data('data_provider_details.json')
    def test_detele_service_worker_success(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get("id", None)
            access_urls = provider_detail_dict.get("access_urls", None)
            status = provider_detail_dict.get("status", u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return_mock = {
                    'CloudFront': {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                    }
                }
                service_controller = mock.Mock(
                    delete=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='CloudFront',
                    service_controller=service_controller)
                )
            elif name == 'maxcdn':
                return_mock = {
                    'MaxCDN': {'id': "pullzone345"}
                }
                service_controller = mock.Mock(
                    delete=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name='MaxCDN',
                    service_controller=service_controller)
                )
            else:
                return_mock = {
                    name.title(): {
                        'id':
                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                    }
                }
                service_controller = mock.Mock(
                    delete=mock.Mock(return_value=return_mock)
                )
                return mock.Mock(obj=mock.Mock(
                    provider_name=name.title(),
                    service_controller=service_controller)
                )

        providers.__getitem__.side_effect = get_provider_extension_by_name

        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):
            self.mock_delete_service()

    @ddt.file_data('data_provider_details.json')
    def test_delete_service_worker_with_error(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get("id", None)
            access_urls = provider_detail_dict.get("access_urls", None)
            status = provider_detail_dict.get("status", u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name='CloudFront',
                        service_controller=mock.Mock(
                            delete=mock.Mock(
                                return_value={
                                    'CloudFront': {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))
            elif name == 'maxcdn':
                return mock.Mock(obj=mock.Mock(
                    provider_name='MaxCDN',
                    service_controller=mock.Mock(
                        delete=mock.Mock(return_value={
                            'MaxCDN': {'error': "fail to create servcice",
                                       'error_detail':
                                       'MaxCDN delete service'
                                       ' failed because of XYZ'}})
                    )
                ))
            else:
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name=name.title(),
                        service_controller=mock.Mock(
                            delete=mock.Mock(
                                return_value={
                                    name.title(): {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))

        providers.__getitem__.side_effect = get_provider_extension_by_name

        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):
            self.mock_delete_service()

    @ddt.file_data('data_provider_details.json')
    def test_purge(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        self.sc.storage_controller.get_provider_details.return_value = (
            self.provider_details
        )

        self.service_obj.provider_details = self.provider_details
        self.sc.storage_controller.get.return_value = (
            self.service_obj
        )

        self.sc.purge(self.project_id, self.service_id, None)

        # ensure the manager calls the storage driver with the appropriate data
        sc = self.sc.storage_controller
        sc.get_provider_details.assert_called_once_with(
            self.project_id,
            self.service_id,
        )

    @ddt.file_data('data_provider_details.json')
    def test_purge_service_worker_success(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get("id", None)
            access_urls = provider_detail_dict.get("access_urls", None)
            status = provider_detail_dict.get("status", u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name='CloudFront',
                        service_controller=mock.Mock(
                            purge=mock.Mock(
                                return_value={
                                    'CloudFront': {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))
            elif name == 'maxcdn':
                return mock.Mock(obj=mock.Mock(
                    provider_name='MaxCDN',
                    service_controller=mock.Mock(
                        purge=mock.Mock(return_value={
                            'MaxCDN': {
                                'id':
                                '08d2e326-377e-11e4-b531-3c15c2b8d2d6'
                            }
                        })
                    )
                ))
            else:
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name=name.title(),
                        service_controller=mock.Mock(
                            purge=mock.Mock(
                                return_value={
                                    name.title(): {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))

        providers.__getitem__.side_effect = get_provider_extension_by_name

        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):
            self.mock_purge_service()

    @ddt.file_data('data_provider_details.json')
    def test_purge_service_worker_with_error(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get("id", None)
            access_urls = provider_detail_dict.get("access_urls", None)
            status = provider_detail_dict.get("status", u'deployed')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        providers = self.sc._driver.providers

        def get_provider_extension_by_name(name):
            if name == 'cloudfront':
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name='CloudFront',
                        service_controller=mock.Mock(
                            purge=mock.Mock(
                                return_value={
                                    'CloudFront': {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))
            else:
                return mock.Mock(
                    obj=mock.Mock(
                        provider_name=name.title(),
                        service_controller=mock.Mock(
                            purge=mock.Mock(
                                return_value={
                                    name.title(): {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                    }}),
                        )))

        providers.__getitem__.side_effect = get_provider_extension_by_name

        with MonkeyPatchControllers(self.sc,
                                    self.sc.dns_controller,
                                    self.sc.storage_controller,
                                    memoized_controllers.task_controllers):
            self.mock_purge_service()
