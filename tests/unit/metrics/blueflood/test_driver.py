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

from poppy.metrics.blueflood import driver
from tests.unit import base


class TestBlueFloodMetricsDriver(base.TestCase):

    def setUp(self):
        super(TestBlueFloodMetricsDriver, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.metrics_driver = (
            driver.BlueFloodMetricsDriver(self.conf))

    def test_init(self):
        self.assertTrue(self.metrics_driver is not None)

    def test_vendor_name(self):
        self.assertEqual('BlueFlood', self.metrics_driver.metrics_driver_name)

    def test_is_alive(self):
        self.assertEqual(True, self.metrics_driver.is_alive())

    def test_service_contoller(self):
        self.assertTrue(self.metrics_driver.services_controller
                        is not None)
