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

import ddt
import mock
from oslo.config import cfg

from poppy.manager.default import driver
from poppy.manager.default import services
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

    def test_create(self):
        project_id = 'mock_id'
        service_name = 'mock_service'
        service_json = ''

        self.sc.create(project_id, service_name, service_json)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage.create.assert_called_once_with(project_id,
                                                       service_name,
                                                       service_json)
        # and that the providers are notified.
        providers = self.sc._driver.providers
        providers.map.assert_called_once_with(self.sc.provider_wrapper.create,
                                              service_name,
                                              service_json)

    @ddt.file_data('data_provider_details.json')
    def test_update(self, provider_details_json):
        self.provider_details = provider_details_json
        project_id = 'mock_id'
        service_name = 'mock_service'
        service_json = ''

        providers = self.sc._driver.providers

        self.sc.storage.get_provider_details.return_value = (
            self.provider_details
        )

        self.sc.update(project_id, service_name, service_json)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage.update.assert_called_once_with(project_id,
                                                       service_name,
                                                       service_json)
        # and that the providers are notified.
        providers.map.assert_called_once_with(self.sc.provider_wrapper.update,
                                              self.provider_details,
                                              service_json)

    @ddt.file_data('data_provider_details.json')
    def test_delete(self, provider_details_json):
        self.provider_details = provider_details_json
        project_id = 'mock_id'
        service_name = 'mock_service'

        self.sc.storage.get_provider_details.return_value = (
            self.provider_details
        )

        self.sc.delete(project_id, service_name)

        # ensure the manager calls the storage driver with the appropriate data
        self.sc.storage.delete.assert_called_once_with(project_id,
                                                       service_name)
        # and that the providers are notified.
        providers = self.sc._driver.providers
        providers.map.assert_called_once_with(self.sc.provider_wrapper.delete,
                                              self.provider_details)
