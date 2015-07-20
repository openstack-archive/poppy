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

"""Unittests for Rackspace DNS Provider implementation."""

import mock
from oslo_config import cfg
import pyrax

from poppy.dns.rackspace import driver
from poppy.dns.rackspace.helpers import retry_exceptions
from tests.unit import base

RACKSPACE_OPTIONS = [
    cfg.StrOpt('username', default='',
               help='Keystone Username'),
    cfg.StrOpt('api_key', default='',
               help='Keystone API Key'),
    cfg.BoolOpt('sharding_enabled', default=True,
                help='Enable Sharding?'),
    cfg.IntOpt('num_shards', default=10, help='Number of Shards to use'),
    cfg.StrOpt('shard_prefix', default='cdn',
               help='The shard prefix to use'),
    cfg.StrOpt('url', default='',
               help='The url for customers to CNAME to'),
    cfg.StrOpt('email', help='The email to be provided to Rackspace DNS for'
               'creating subdomains'),
    cfg.StrOpt('auth_endpoint', default='',
               help='Authentication end point for DNS'),
    cfg.IntOpt('timeout', default=30, help='DNS response timeout'),
    cfg.IntOpt('delay', default=1, help='DNS retry delay'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_init(self, mock_set_credentials):
        pyrax.cloud_dns = mock.Mock()
        provider = driver.DNSProvider(self.conf)
        mock_set_credentials.assert_called_once_with(
            provider._conf['drivers:dns:rackspace'].username,
            provider._conf['drivers:dns:rackspace'].api_key)

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_is_alive(self, mock_set_credentials):
        """Happy path test for checking the health of DNS."""
        provider = driver.DNSProvider(self.conf)
        provider.rackdns_client = mock.Mock()
        self.assertTrue(provider.is_alive())

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_is_alive_dns_down(self, mock_set_credentials):
        """Negative test for checking the health of DNS."""
        provider = driver.DNSProvider(self.conf)
        provider.rackdns_client = mock.Mock()
        provider.rackdns_client.list = mock.Mock(side_effect=Exception('foo'))
        self.assertFalse(provider.is_alive())

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_wrong_credentials(self, mock_set_credentials):
        """Negative test for checking the health of DNS."""
        mock_set_credentials.side_effect = pyrax.exc.AuthenticationFailed(
            "Incorrect/unauthorized credentials received")

        self.assertRaises(pyrax.exc.AuthenticationFailed,
                          driver.DNSProvider,
                          self.conf)

    @mock.patch('pyrax.set_credentials')
    @mock.patch('pyrax.set_setting')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_get_client(self, mock_set_credentials, mock_set_setting):
        pyrax.cloud_dns = mock.Mock()
        provider = driver.DNSProvider(self.conf)
        client = provider.client
        self.assertNotEqual(client, None)

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_service_controller(self, mock_set_credentials):
        provider = driver.DNSProvider(self.conf)
        self.assertNotEqual(provider.services_controller, None)

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def test_retry_exceptions(self, mock_set_credentials):
        provider = driver.DNSProvider(self.conf)
        self.assertEqual(provider.retry_exceptions, retry_exceptions)
