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

from oslo.config import cfg

from cdn.transport.pecan import driver
from tests.unit.utils import base
from tests.unit.utils import thread_helper


class TestPecanDriver(base.UnitTestBase):

    def setUp(self):
        # Let manager = None for now
        self.pecan_driver = driver.PecanTransportDriver(cfg.CONF, None)
        super(TestPecanDriver, self).setUp()

    def test_app_created(self):
        self.assertEquals(self.pecan_driver.app is not None, True)
        t = thread_helper.StoppableThread(target=self.pecan_driver.listen)
        t.start()
        self.assertTrue(t.isAlive())
        t.stop()
        thread_helper.terminate_thread(t)
