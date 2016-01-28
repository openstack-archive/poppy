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

"""Unittests for BlueFlood metrics service_controller."""

import mock
from oslo_config import cfg

from poppy.metrics.blueflood import driver
from tests.unit import base

from hypothesis import given
from hypothesis import strategies


class TestBlueFloodServiceController(base.TestCase):

    def setUp(self):
        super(TestBlueFloodServiceController, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.metrics_driver = (
            driver.BlueFloodMetricsDriver(self.conf))

    @given(strategies.text(), strategies.integers(),
           strategies.integers(), strategies.integers())
    def test_read(self, metric_name, from_timestamp, to_timestamp, resolution):
        self.metrics_driver.services_controller.__class__.read = \
            mock.Mock(return_value='success')

        self.metrics_driver.services_controller.read(
            metric_name=metric_name,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            resolution=resolution
        )
        self.metrics_driver.services_controller.read.assert_called_once_with(
            metric_name=metric_name,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            resolution=resolution
        )
