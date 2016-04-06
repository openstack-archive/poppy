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

import ddt
import mock
from oslo_config import cfg

from poppy.provider.akamai import driver
from tests.unit import base

AKAMAI_OPTIONS = [
    # credentials && base URL for policy API
    cfg.StrOpt(
        'policy_api_client_token',
        help='Akamai client token for policy API'),
    cfg.StrOpt(
        'policy_api_client_secret',
        help='Akamai client secret for policy API'),
    cfg.StrOpt(
        'policy_api_access_token',
        help='Akamai access token for policy API'),
    cfg.StrOpt(
        'policy_api_base_url', default='http://abc/',
        help='Akamai policy API base URL'),
    # credentials && base URL for CCU API
    # for purging
    cfg.StrOpt(
        'ccu_api_client_token',
        help='Akamai client token for CCU API'),
    cfg.StrOpt(
        'ccu_api_client_secret',
        help='Akamai client secret for CCU API'),
    cfg.StrOpt(
        'ccu_api_access_token',
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
        'akamai_https_shared_config_number',
        default=str(random.randint(10000, 99999)),
        help='Akamai configuration number for shared wildcard https policies'),
    cfg.ListOpt(
        'akamai_https_san_config_numbers',
        default=[str(random.randint(10000, 99999))],
        help='A list of Akamai configuration number for '
             'SAN cert https policies'
    ),
    cfg.ListOpt(
        'akamai_https_custom_config_numbers',
        default=[str(random.randint(10000, 99999))],
        help='A list of Akamai configuration number for '
             'Custom cert https policies'
    ),

    # SANCERT related configs
    cfg.ListOpt('san_cert_cnames', default='secure.san.test.com',
                help='A list of san certs cnamehost names'),
    cfg.IntOpt('san_cert_hostname_limit', default=80,
               help='default limit on how many hostnames can'
               ' be held by a SAN cert'),
    cfg.StrOpt('cert_info_storage_type',
               default='zookeeper',
               help='Storage type for storing san cert information'),

    # related info for SPS && PAPI APIs
    cfg.StrOpt(
        'contract_id',
        help='Operator contractID'),
    cfg.StrOpt(
        'group_id',
        help='Operator groupID'),
    cfg.StrOpt(
        'property_id',
        help='Operator propertyID'),


    # Metrics related configs
    cfg.IntOpt('metrics_resolution',
               help='Resolution in seconds for retrieving metrics',
               default=86400)
]


class Response(object):

    def __init__(self, status_code, text, resp_status):
        self._status_code = status_code
        self._text = text
        self.resp_status = resp_status

    @property
    def ok(self):
        return self.resp_status

    @property
    def status_code(self):
        return self._status_code

    @property
    def text(self):
        return self._text


@ddt.ddt
class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient'
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

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

    @ddt.data((200, 'Put Successful', True), (500, 'Put Failed', False))
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_is_alive(self, details):
        status_code, text, health_status = details
        provider = driver.CDNProvider(self.conf)
        mock_api_client = provider.service_controller.driver.policy_api_client
        resp = Response(status_code, text, health_status)
        with mock.patch.object(mock_api_client, 'put',
                               return_value=resp):
            self.assertEqual(health_status, provider.is_alive())

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_get_client(self, mock_connect):
        mock_connect.return_value = mock.Mock()
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(None, provider.policy_api_client)
        self.assertNotEqual(None, provider.ccu_api_client)

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_cert_info_storage(self, mock_connect):
        mock_connect.return_value = mock.Mock()
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(None, provider.cert_info_storage)
