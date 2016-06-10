# Copyright (c) 2016 Rackspace, Inc.
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

"""Unittests for Default DNS Provider implementation."""

from oslo_config import cfg

from poppy.dns.default import driver
from poppy.dns.default.helpers import retry_exceptions
from tests.unit import base


class TestDefaultDNSDriver(base.TestCase):

    def setUp(self):
        super(TestDefaultDNSDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    def test_is_alive(self):
        provider = driver.DNSProvider(self.conf)
        self.assertTrue(provider.is_alive())

    def test_get_client(self):
        provider = driver.DNSProvider(self.conf)
        self.assertIsNone(provider.client)

    def test_service_controller(self):
        provider = driver.DNSProvider(self.conf)
        self.assertNotEqual(provider.services_controller, None)

    def test_retry_exceptions(self):
        provider = driver.DNSProvider(self.conf)
        self.assertEqual(provider.retry_exceptions, retry_exceptions)
