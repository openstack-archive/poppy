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

from poppy.provider.mock import services
from tests.unit import base


@ddt.ddt
class MockProviderServicesTest(base.TestCase):

    @mock.patch('poppy.provider.mock.driver.CDNProvider')
    def setUp(self, mock_driver):
        super(MockProviderServicesTest, self).setUp()
        self.driver = mock_driver()
        self.test_provider_service_id = 73432
        self.sc = services.ServiceController(self.driver)

    @ddt.file_data('data_service.json')
    def test_update(self, service_json):
        response = self.sc.update(self.test_provider_service_id, service_json)
        self.assertTrue(response is not None)

    def test_delete(self):
        response = self.sc.delete(self.test_provider_service_id)
        self.assertTrue(response is not None)
    
    def test_get(self):
        response = self.sc.get("mock_name")
        self.assertTrue(response is not None)
    
    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        response = self.sc.create("mock_name", service_json)
        self.assertTrue(response is not None)

