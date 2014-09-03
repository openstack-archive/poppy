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

import mock
from oslo.config import cfg

from poppy.manager.default import driver
from poppy.manager.default import services
from poppy.provider.mock import driver as mock_provider
from tests.unit import base


class DefaultManagerDriverTests(base.TestCase):
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.provider.base.driver.ProviderDriverBase')
    @mock.patch('poppy.provider.mock.driver.CDNProvider')
    def setUp(self, mock_storage, mock_provider, mock_mock_provider):
        super(DefaultManagerDriverTests, self).setUp()
        self.mock_storage = mock_storage
        self.mock_provider = mock_provider
        self.mock_mock_provider = mock_mock_provider
        conf = cfg.ConfigOpts()
        self.driver = driver.DefaultManagerDriver(conf,
                                                  mock_storage,
                                                  mock_mock_provider)

    def test_health_storage_not_available(self):
        self.mock_storage.is_alive.return_value = False
        status, body = self.driver.health()
        self.assertEqual('404', status)
        self.assertEqual('Storage not available', body['storage'])

    def test_health_provider_not_available(self):
        #mock.patch.object(self.driver, 'providers')
        self.mock_mock_provider.health.return_value = False
        #import pdb; pdb.set_trace()
        status, body = self.driver.health()
        self.assertEqual('404', status)

    def test_services_controller(self):
        sc = self.driver.services_controller

        self.assertIsInstance(sc, services.DefaultServicesController)
