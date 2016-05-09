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

"""Unittests for BlueFlood Helper"""

from dateutil import parser
import ddt

from poppy.metrics.blueflood.utils import helper
from tests.unit import base


@ddt.ddt
class TestBlueFloodHelper(base.TestCase):

    def setUp(self):
        super(TestBlueFloodHelper, self).setUp()

        pass

    @ddt.data("2016-05-09T18:04:18Z")
    def test_datetime_to_epoch(self, value):
        dt = parser.parse(value)
        epoch_value = helper.datetime_to_epoch(dt)

        # assert value is correctly converted (msec in GMT timezone)
        self.assertEqual(int(epoch_value), 1462817058000)

    @ddt.data("1462817058")
    def test_datetime_from_epoch(self, value):
        dt = helper.datetime_from_epoch(int(value) * 1000)

        # in GMT timezone
        self.assertEqual("2016-05-09T18:04:18", dt)
