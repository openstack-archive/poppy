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

from boto import cloudfront
import ddt
import mock


from poppy.provider.cloudfront import services
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('poppy.provider.cloudfront.services.ServiceController.client')
    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    def setUp(self, mock_get_client, MockDriver):
        super(TestServices, self).setUp()

        self.service_name = 'myservice'
        self.mock_get_client = mock_get_client
        self.driver = MockDriver()
        self.controller = services.ServiceController(self.driver)

    @ddt.file_data('data_service.json')
    def test_create_server_error(self, service_json):
        # create_distribution: CloudFrontServerError
        side_effect = cloudfront.exception.CloudFrontServerError(
            503, 'Service Unavailable')
        self.controller.client.create_distribution.side_effect = side_effect

        resp = self.controller.create(self.service_name, service_json)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_exception(self, service_json):
        # generic exception: Exception
        self.controller.client.create_distribution.side_effect = Exception(
            'Creating service failed.')
        resp = self.controller.create(self.service_name, service_json)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        # clear run
        resp = self.controller.create(self.service_name, service_json)
        self.assertIn('links', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_update(self, service_json):
        resp = self.controller.update(self.service_name, service_json)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_delete_exceptions(self):
        # delete_distribution: Exception
        self.controller.client.delete_distribution.side_effect = Exception(
            'Creating service failed.')
        resp = self.controller.delete(self.service_name)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
        resp = self.controller.delete(self.service_name)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_client(self):
        self.assertNotEqual(self.controller.client(), None)
