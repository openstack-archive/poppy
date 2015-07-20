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

import os

import mock
from oslo_config import cfg

from poppy.common import util
from poppy.provider.maxcdn import driver
from tests.unit import base


MAXCDN_OPTIONS = [
    cfg.StrOpt('alias', help='MAXCDN API account alias'),
    cfg.StrOpt('consumer_key', help='MAXCDN API consumer key'),
    cfg.StrOpt('consumer_secret', help='MAXCDN API consumer secret'),
]


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))))
        conf_path = os.path.join(tests_path, 'etc', 'default_functional.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])

        self.conf = cfg.CONF

    @mock.patch('maxcdn.MaxCDN')
    @mock.patch.object(driver, 'MAXCDN_OPTIONS', new=MAXCDN_OPTIONS)
    def test_init(self, mock_connect):
        provider = driver.CDNProvider(self.conf)
        mock_connect.assert_called_once_with(
            provider._conf['drivers:provider:maxcdn'].alias,
            provider._conf['drivers:provider:maxcdn'].consumer_key,
            provider._conf['drivers:provider:maxcdn'].consumer_secret)

    @mock.patch('requests.get')
    @mock.patch.object(driver, 'MAXCDN_OPTIONS', new=MAXCDN_OPTIONS)
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

    @mock.patch.object(driver, 'MAXCDN_OPTIONS', new=MAXCDN_OPTIONS)
    def test_get_client(self):
        provider = driver.CDNProvider(self.conf)
        client = provider.client
        self.assertNotEqual(client, None)

    @mock.patch('poppy.provider.maxcdn.controllers.ServiceController')
    @mock.patch.object(driver, 'MAXCDN_OPTIONS', new=MAXCDN_OPTIONS)
    def test_service_controller(self, MockController):
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(provider.service_controller, None)
