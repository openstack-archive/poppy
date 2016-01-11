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

"""Unittests for cloud_metrics cache driver implementation."""

from oslo_config import cfg

from poppy.cache.cloud_metrics import driver
from tests.unit import base


class TestCacheDriver(base.TestCase):

    def setUp(self):
        super(TestCacheDriver, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.cache_driver = (
            driver.CloudMetricsCacheDriver(self.conf))

    def test_init(self):
        self.assertTrue(self.cache_driver is not None)

    def test_vendor_name(self):
        self.assertEqual('Cloud Metrics', self.cache_driver.vendor_name)

    def test_is_alive(self):
        self.assertEqual(True, self.cache_driver.is_alive())

    def test_service_contoller(self):
        self.assertTrue(self.cache_driver.services_controller
                        is not None)
