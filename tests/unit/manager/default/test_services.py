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

import ddt
import mock
from oslo.config import cfg

from poppy.manager.default import driver
from poppy.manager.default import services
from poppy.model import flavor
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class DefaultManagerServiceTests(base.TestCase):

    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.provider.base.driver.ProviderDriverBase')
    def setUp(self, mock_driver, mock_provider):
        super(DefaultManagerServiceTests, self).setUp()

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        manager_driver = driver.DefaultManagerDriver(conf,
                                                     mock_driver,
                                                     mock_provider)

        # stubbed driver
        self.sc = services.DefaultServicesController(manager_driver)

        self.project_id = 'mock_id'
        self.service_name = 'mock_service'
        self.service_json = {
            "name": "fake_service_name",
            "domains": [
                {"domain": "www.mywebsite.com"},
                {"domain": "blog.mywebsite.com"},
            ],
            "origins": [
                {
                    "origin": "mywebsite.com",
                    "port": 80,
                    "ssl": False
                },
                {
                    "origin": "mywebsite.com",
                }
            ],
            "caching": [
                {"name": "default", "ttl": 3600},
                {"name": "home",
                 "ttl": 17200,
                 "rules": [
                     {"name": "index", "request_url": "/index.htm"}
                 ]
                 },
                {"name": "images",
                 "ttl": 12800,
                 }
            ],
            "flavorRef": "https://www.poppycdn.io/v1.0/flavors/standard"
        }

    def test_create(self):
        service_obj = service.load_from_json(self.service_json)
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
                return mock.Mock(
                    obj=mock.Mock(
                        service_controller=mock.Mock(
                            create=mock.Mock(
                                return_value={
                                    'Cloudfront': {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                        'links': [
                                            {
                                                'href': 'www.mysite.com',
                                                'rel': 'access_url'}],
                                        'status': "in_progress"}}),
                        )))
            elif name == "fastly":
                return mock.Mock(obj=mock.Mock(service_controller=mock.Mock(
                    create=mock.Mock(return_value={
                        'Fastly': {'error': "fail to create servcice",
                                   'error_detail': 'Fastly Create failed'
                                   ' because of XYZ'}})
                    )
                ))
            else:
                return mock.Mock(
                    obj=mock.Mock(
                        service_controller=mock.Mock(
                            create=mock.Mock(
                                return_value={
                                    name.title(): {
                                        'id':
                                        '08d2e326-377e-11e4-b531-3c15c2b8d2d6',
                                        'links': [
                                            {
                                                'href': 'www.mysite.com',
                                                'rel': 'access_url'}]}}),
                        )))

        providers.__getitem__.side_effect = get_provider_extension_by_name

        self.sc.create(self.project_id, service_obj)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage_controller.create.assert_called_once_with(
            self.project_id,
            service_obj)

    @ddt.file_data('data_provider_details.json')
    def test_update(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get(
                "provider_service_id", None)
            access_urls = provider_detail_dict.get("access_url", None)
            status = provider_detail_dict.get("status", u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        providers = self.sc._driver.providers

        self.sc.storage_controller.get_provider_details.return_value = (
            self.provider_details
        )

        self.sc.update(self.project_id, self.service_name, self.service_json)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage_controller.update.assert_called_once_with(
            self.project_id,
            self.service_name,
            self.service_json)
        # and that the providers are notified.
        providers.map.assert_called_once_with(self.sc.provider_wrapper.update,
                                              self.provider_details,
                                              self.service_json)

    @ddt.file_data('data_provider_details.json')
    def test_delete(self, provider_details_json):
        self.provider_details = {}
        for provider_name in provider_details_json:
            provider_detail_dict = json.loads(
                provider_details_json[provider_name]
            )
            provider_service_id = provider_detail_dict.get(
                "provider_service_id", None)
            access_urls = provider_detail_dict.get("access_urls", None)
            status = provider_detail_dict.get("status", u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            self.provider_details[provider_name] = provider_detail_obj

        self.sc.storage_controller.get_provider_details.return_value = (
            self.provider_details
        )

        self.sc.delete(self.project_id, self.service_name)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage_controller.delete.assert_called_once_with(
            self.project_id,
            self.service_name
        )
        # and that the providers are notified.
        providers = self.sc._driver.providers
        providers.map.assert_called_once_with(self.sc.provider_wrapper.delete,
                                              self.provider_details)
