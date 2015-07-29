# Copyright (c) 2015 Rackspace, Inc.
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
import uuid

import mock
from taskflow import engines

from poppy.distributed_task.taskflow.flow import create_service
from poppy.distributed_task.taskflow.flow import create_ssl_certificate
from poppy.distributed_task.taskflow.flow import delete_service
from poppy.distributed_task.taskflow.flow import purge_service
from poppy.distributed_task.taskflow.flow import update_service
from poppy.distributed_task.taskflow.flow import update_service_state
from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model import service
from poppy.model import ssl_certificate
from tests.unit import base
from tests.unit.manager.default.test_services import MonkeyPatchControllers


class DNSException(Exception):
    pass


class TestFlowRuns(base.TestCase):

    def setUp(self):
        super(TestFlowRuns, self).setUp()
        self.time_factor = 0.001
        self.total_retries = 5

    def all_controllers(self):
        service_controller, storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_controller, dns_controller = \
            memoized_controllers.task_controllers('poppy', 'dns')
        return service_controller, storage_controller, dns_controller

    def dns_exceptions(self):
        # NOTE(TheSriram): create a chain of mocked return values,
        # to allow for retries, and finally succeed. The last value
        # indicating success, is just shown to indicate
        # that exceptions were not thrown.
        dns_responder_returns = [
            [
                {
                    'cdn_provider':
                        {
                            'error': 'DNSException',
                            'error_class': 'tests.unit.distributed_task'
                                           '.taskflow.test_flows.DNSException'
                        }
                }
            ],
            [
                {
                    'cdn_provider':
                        {
                            'error': 'DNSException',
                            'error_class': 'tests.unit.distributed_task'
                                           '.taskflow.test_flows.DNSException'
                        }
                }
            ],
            [
                {
                    'cdn_provider':
                        {
                            'error': 'DNSException',
                            'error_class': 'tests.unit.distributed_task'
                                           '.taskflow.test_flows.DNSException'
                        }
                }
            ],
            [
                {
                    'cdn_provider':
                        {
                            'success': 'True',
                        }
                }
            ],
        ]

        return dns_responder_returns

    def patch_create_flow(self, service_controller,
                          storage_controller, dns_controller):
        storage_controller.get = mock.Mock()
        storage_controller.update = mock.Mock()
        storage_controller._driver.close_connection = mock.Mock()
        service_controller.provider_wrapper.create = mock.Mock()
        service_controller.provider_wrapper.create._mock_return_value = []
        service_controller._driver = mock.Mock()
        service_controller._driver.providers.__getitem__ = mock.Mock()
        dns_controller.create = mock.Mock()
        dns_controller.create._mock_return_value = []
        common.create_log_delivery_container = mock.Mock()

    def patch_update_flow(self, service_controller,
                          storage_controller, dns_controller):
        storage_controller.get = mock.Mock()
        storage_controller.update = mock.Mock()
        storage_controller._driver.close_connection = mock.Mock()
        service_controller.provider_wrapper.update = mock.Mock()
        service_controller.provider_wrapper.update._mock_return_value = []
        service_controller._driver = mock.Mock()
        service_controller._driver.providers.__getitem__ = mock.Mock()
        dns_controller.update = mock.Mock()
        dns_controller.update._mock_return_value = []
        common.create_log_delivery_container = mock.Mock()

    def patch_delete_flow(self, service_controller,
                          storage_controller, dns_controller):
        storage_controller.get = mock.Mock()
        storage_controller.update = mock.Mock()
        storage_controller.delete = mock.Mock()
        storage_controller._driver.close_connection = mock.Mock()
        service_controller.provider_wrapper.delete = mock.Mock()
        service_controller.provider_wrapper.delete._mock_return_value = []
        service_controller._driver = mock.Mock()
        service_controller._driver.providers.__getitem__ = mock.Mock()
        dns_controller.update = mock.Mock()
        dns_controller.update._mock_return_value = []

    def patch_purge_flow(self, service_controller,
                         storage_controller, dns_controller):
        storage_controller.get = mock.Mock()
        storage_controller.update = mock.Mock()
        storage_controller.delete = mock.Mock()
        storage_controller._driver.close_connection = mock.Mock()
        service_controller.provider_wrapper.purge = mock.Mock()
        service_controller.provider_wrapper.purge._mock_return_value = []
        service_controller._driver = mock.Mock()
        service_controller._driver.providers.__getitem__ = mock.Mock()

    def patch_service_state_flow(self, service_controller,
                                 storage_controller, dns_controller):
        storage_controller.update_state = mock.Mock()
        dns_controller.enable = mock.Mock()
        dns_controller.disable = mock.Mock()

    def patch_create_ssl_certificate_flow(self, service_controller,
                                          storage_controller, dns_controller):
        storage_controller.get = mock.Mock()
        storage_controller.update = mock.Mock()
        storage_controller._driver.close_connection = mock.Mock()
        service_controller.provider_wrapper.create_certificate = mock.Mock()
        service_controller.provider_wrapper.create_certificate.\
            _mock_return_value = []
        service_controller._driver = mock.Mock()
        service_controller._driver.providers.__getitem__ = mock.Mock()
        service_controller._driver.notification = [mock.Mock()]
        dns_controller.create = mock.Mock()
        dns_controller.create._mock_return_value = []
        common.create_log_delivery_container = mock.Mock()

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_create_flow_normal(self, mock_creds, mock_dns_client):
        providers = ['cdn_provider']
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(str(uuid.uuid4())),
            'time_seconds': [i * self.time_factor
                             for i in range(self.total_retries)]
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_create_flow(service_controller,
                                   storage_controller,
                                   dns_controller)
            engines.run(create_service.create_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_update_flow_normal(self, mock_creds, mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        domains_new = domain.Domain(domain='mycdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_old = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')
        service_new = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_new],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor
                             for i in range(self.total_retries)],
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict())
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_update_flow(service_controller, storage_controller,
                                   dns_controller)
            engines.run(update_service.update_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_delete_flow_normal(self, mock_creds, mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)],
            'provider_details': json.dumps(
                dict([(k, v.to_dict())
                      for k, v in service_obj.provider_details.items()]))
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_delete_flow(service_controller, storage_controller,
                                   dns_controller)
            engines.run(delete_service.delete_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_purge_flow_normal(self, mock_creds, mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'provider_details': json.dumps(
                dict([(k, v.to_dict())
                      for k, v in service_obj.provider_details.items()])),
            'purge_url': 'cdn.poppy.org',
            'hard': json.dumps(True),
            'service_obj': json.dumps(service_obj.to_dict())
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_purge_flow(service_controller, storage_controller,
                                  dns_controller)
            engines.run(purge_service.purge_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_service_state_flow_normal(self, mock_creds,
                                       mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'state': 'enable',
            'service_obj': json.dumps(service_obj.to_dict())
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_service_state_flow(service_controller,
                                          storage_controller,
                                          dns_controller)
            engines.run(update_service_state.enable_service(), store=kwargs)
            engines.run(update_service_state.disable_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_create_flow_dns_exception(self, mock_creds,
                                       mock_dns_client):
        providers = ['cdn_provider']
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(str(uuid.uuid4())),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)]
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_create_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.create = mock.Mock()
            dns_controller.create._mock_return_value = {
                'cdn_provider': {
                    'error': 'Whoops!',
                    'error_class': 'tests.unit.distributed_task'
                                   '.taskflow.test_flows.DNSException'
                }
            }
            engines.run(create_service.create_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_update_flow_dns_exception(self, mock_creds,
                                       mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        domains_new = domain.Domain(domain='mycdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_old = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')
        service_new = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_new],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)],
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict())
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_update_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.update = mock.Mock()
            dns_controller.update._mock_return_value = {
                'cdn_provider': {
                    'error': 'Whoops!',
                    'error_class': 'tests.unit.distributed_task'
                                   '.taskflow.test_flows.DNSException'
                }
            }

            engines.run(update_service.update_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_delete_flow_dns_exception(self, mock_creds,
                                       mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)],
            'provider_details': json.dumps(
                dict([(k, v.to_dict())
                      for k, v in service_obj.provider_details.items()]))
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_delete_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.delete = mock.Mock()
            dns_controller.delete._mock_return_value = {
                'cdn_provider': {
                    'error': 'Whoops!',
                    'error_class': 'tests.unit.distributed_task'
                                   '.taskflow.test_flows.DNSException'
                }
            }

            engines.run(delete_service.delete_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_update_flow_dns_exception_with_retry(self, mock_creds,
                                                  mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        domains_new = domain.Domain(domain='mycdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_old = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')
        service_new = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_new],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)],
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict())
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_update_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.update = mock.Mock()
            dns_responder_returns = self.dns_exceptions()

            dns_controller.update._mock_side_effect = (dns_responder for
                                                       dns_responder in
                                                       dns_responder_returns)

            engines.run(update_service.update_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_create_flow_dns_exception_with_retry(self,
                                                  mock_creds,
                                                  mock_dns_client):
        providers = ['cdn_provider']
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': json.dumps(str(uuid.uuid4())),
            'auth_token': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(str(uuid.uuid4())),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)]
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_create_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.create = mock.Mock()

            dns_responder_returns = self.dns_exceptions()

            dns_controller.create._mock_side_effect = (dns_responder for
                                                       dns_responder in
                                                       dns_responder_returns)

            engines.run(create_service.create_service(), store=kwargs)

    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_delete_flow_dns_exception_with_retry(self,
                                                  mock_creds,
                                                  mock_dns_client):
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = service.Service(service_id=service_id,
                                      name='poppy cdn service',
                                      domains=[domains_old],
                                      origins=[current_origin],
                                      flavor_id='cdn')

        kwargs = {
            'project_id': json.dumps(str(uuid.uuid4())),
            'service_id': json.dumps(service_id),
            'time_seconds': [i * self.time_factor for
                             i in range(self.total_retries)],
            'provider_details': json.dumps(
                dict([(k, v.to_dict())
                      for k, v in service_obj.provider_details.items()]))
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):

            self.patch_delete_flow(service_controller, storage_controller,
                                   dns_controller)
            dns_controller.delete = mock.Mock()
            dns_responder_returns = self.dns_exceptions()

            dns_controller.delete._mock_side_effect = (dns_responder for
                                                       dns_responder in
                                                       dns_responder_returns)
            engines.run(delete_service.delete_service(), store=kwargs)

    # Keep create credentials for now
    @mock.patch('pyrax.cloud_dns')
    @mock.patch('pyrax.set_credentials')
    def test_create_ssl_certificate_normal(self, mock_creds, mock_dns_client):
        providers = ['cdn_provider']
        cert_obj_json = ssl_certificate.SSLCertificate('cdn',
                                                       'mytestsite.com',
                                                       'san')
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'cert_obj_json': json.dumps(cert_obj_json.to_dict()),
        }

        service_controller, storage_controller, dns_controller = \
            self.all_controllers()

        with MonkeyPatchControllers(service_controller,
                                    dns_controller,
                                    storage_controller,
                                    memoized_controllers.task_controllers):
            self.patch_create_ssl_certificate_flow(service_controller,
                                                   storage_controller,
                                                   dns_controller)
            engines.run(create_ssl_certificate.create_ssl_certificate(),
                        store=kwargs)
