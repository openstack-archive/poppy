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

import random

import mock
from oslo.config import cfg

from poppy.provider.akamai import driver
from tests.unit import base

AKAMAI_OPTIONS = [
    # credentials && base URL for policy API
    cfg.StrOpt(
        'policy_api_client_token', default='ccc',
        help='Akamai client token for policy API'),
    cfg.StrOpt(
        'policy_api_client_secret', default='sss',
        help='Akamai client secret for policy API'),
    cfg.StrOpt(
        'policy_api_access_token', default='aaa',
        help='Akamai access token for policy API'),
    cfg.StrOpt(
        'policy_api_base_url', default='/abc/',
        help='Akamai policy API base URL'),
    # credentials && base URL for CCU API
    # for purging
    cfg.StrOpt(
        'ccu_api_client_token', default='ccc',
        help='Akamai client token for CCU API'),
    cfg.StrOpt(
        'ccu_api_client_secret', default='sss',
        help='Akamai client secret for CCU API'),
    cfg.StrOpt(
        'ccu_api_access_token', default='aaa',
        help='Akamai access token for CCU API'),
    cfg.StrOpt(
        'ccu_api_base_url', default='/abc/',
        help='Akamai CCU Purge API base URL'),
    # Access URL in Akamai chain
    cfg.StrOpt(
        'akamai_access_url_link', default='abc.def.org',
        help='Akamai domain access_url link'),
    cfg.StrOpt(
        'akamai_https_access_url_suffix', default='ssl.abc',
        help='Akamai domain ssl access url suffix'),
    # Akama client specific configuration numbers
    cfg.StrOpt(
        'akamai_http_config_number', default=str(random.randint(10000, 99999)),
        help='Akamai configuration number for http policies'),
    cfg.StrOpt(
        'akamai_https_config_number',
        default=str(random.randint(10000, 99999)),
        help='Akamai configuration number for https policies'),
]


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_init(self, mock_connect):
        provider = driver.CDNProvider(self.conf)
        akamai_conf = provider._conf['drivers:provider:akamai']
        mock_connect.assert_called_with(
            client_token=(
                akamai_conf.policy_api_client_token),
            client_secret=(
                akamai_conf.policy_api_client_secret),
            access_token=(
                akamai_conf.policy_api_access_token)
        )

        mock_connect.assert_called_with(
            client_token=(
                akamai_conf.ccu_api_client_token),
            client_secret=(
                akamai_conf.ccu_api_client_secret),
            access_token=(
                akamai_conf.ccu_api_access_token)
        )
        self.assertEqual('Akamai', provider.provider_name)

    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_is_alive(self):
        provider = driver.CDNProvider(self.conf)
        self.assertEqual(True, provider.is_alive())

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_get_client(self, mock_connect):
        mock_connect.return_value = mock.Mock()
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(None, provider.policy_api_client)
        self.assertNotEqual(None, provider.ccu_api_client)
