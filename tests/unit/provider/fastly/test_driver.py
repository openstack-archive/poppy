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

import fastly
from oslo.config import cfg

from poppy.provider.fastly import driver
from tests.unit import base


FASTLY_OPTIONS = [
    cfg.StrOpt('apikey',
               default='123456',
               help='Fastly API Key'),
]


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch('fastly.connect')
    @mock.patch.object(driver, 'FASTLY_OPTIONS', new=FASTLY_OPTIONS)
    def test_init(self, mock_connect):
        provider = driver.CDNProvider(self.conf)
        mock_connect.assert_called_once_with(
            provider._conf['drivers:provider:fastly'].apikey)

    @mock.patch.object(driver, 'FASTLY_OPTIONS', new=FASTLY_OPTIONS)
    def test_is_alive(self):
        provider = driver.CDNProvider(self.conf)
        self.assertEqual(provider.is_alive(), True)

    @mock.patch.object(fastly, 'FastlyConnection')
    @mock.patch('fastly.connect')
    @mock.patch.object(driver, 'FASTLY_OPTIONS', new=FASTLY_OPTIONS)
    def test_get_client(self, MockConnection, mock_connect):
        mock_connect.return_value = MockConnection(None, None)
        provider = driver.CDNProvider(self.conf)
        client = provider.client()
        self.assertNotEquals(client, None)

    @mock.patch('poppy.provider.fastly.controllers.ServiceController')
    @mock.patch.object(driver, 'FASTLY_OPTIONS', new=FASTLY_OPTIONS)
    def test_service_controller(self, MockController):
        provider = driver.CDNProvider(self.conf)
        self.assertNotEquals(provider.service_controller, None)
