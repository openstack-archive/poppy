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

"""Unittests for TaskFlow distributed_task service_controller."""

import mock
from oslo_config import cfg

from poppy.cache.cloud_metrics import driver
from tests.unit import base


class TestCacheServiceController(base.TestCase):

    def setUp(self):
        super(TestCacheServiceController, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.cache_driver = (
            driver.CloudMetricsCacheDriver(self.conf))

    def test_read(self):
        self.cache_driver.services_controller.__class__.read = \
            mock.Mock(return_value='success')

        self.cache_driver.services_controller.read(
            metric_name='poppy',
            from_timestamp='infinity',
            to_timestamp='and beyond',
            resolution='4K'
        )
        self.cache_driver.services_controller.read.assert_called_once_with(
            metric_name='poppy',
            from_timestamp='infinity',
            to_timestamp='and beyond',
            resolution='4K'
        )
