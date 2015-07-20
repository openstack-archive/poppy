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


import boto
import mock
from oslo_config import cfg

from poppy.common import util
from poppy.provider.cloudfront import driver
from tests.unit import base


CLOUDFRONT_OPTIONS = [
    cfg.StrOpt('aws_access_key_id',
               default='123456',
               help='CloudFront Access Key ID'),
    cfg.StrOpt('aws_secret_access_key',
               default='123456',
               help='CloudFront Secret Access Key'),
]


@mock.patch.object(driver, 'CLOUDFRONT_OPTIONS', new=CLOUDFRONT_OPTIONS)
class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch('boto.connect_cloudfront')
    def test_init(self, mock_connect):
        provider = driver.CDNProvider(self.conf)
        mock_connect.assert_called_once_with(
            aws_access_key_id=provider._conf[
                'drivers:provider:cloudfront'].aws_access_key_id,
            aws_secret_access_key=provider._conf[
                'drivers:provider:cloudfront'].aws_secret_access_key)

    def test_provider_name(self):
        provider = driver.CDNProvider(self.conf)
        self.assertEqual(provider.provider_name, 'CloudFront')

    @mock.patch('requests.get')
    def test_is_alive(self, mock_get):
        response_object = util.dict2obj(
            {'content': '', 'status_code': 200})
        mock_get.return_value = response_object

        provider = driver.CDNProvider(self.conf)
        self.assertEqual(provider.is_alive(), True)

    @mock.patch('requests.get')
    def test_not_available(self, mock_get):
        response_object = util.dict2obj(
            {'content': 'Not available', 'status_code': 404})
        mock_get.return_value = response_object
        provider = driver.CDNProvider(self.conf)
        self.assertEqual(provider.is_alive(), False)

    @mock.patch.object(boto.cloudfront, 'CloudFrontConnection')
    @mock.patch('boto.connect_cloudfront')
    def test_get_client(self, MockConnection, mock_connect):
        mock_connect.return_value = MockConnection(None, None)
        provider = driver.CDNProvider(self.conf)
        client = provider.client()
        self.assertNotEqual(client, None)

    @mock.patch('poppy.provider.cloudfront.controllers.ServiceController')
    def test_service_controller(self, MockController):
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(provider.service_controller, None)
