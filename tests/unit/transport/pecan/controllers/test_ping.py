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

from poppy.transport.pecan import controllers
import poppy.transport.pecan.controllers.v1.admin
from tests.unit.transport.pecan.controllers import base


class PingControllerTests(base.BasePecanControllerUnitTest):

    def setUp(self):
        super(PingControllerTests, self).setUp(
            poppy.transport.pecan.controllers.v1.admin
        )

        self.controller = controllers.v1.ping.PingController(self.driver)
        self.manager = self.driver.manager

    def test_ping_not_alive(self):
        self.manager.health_controller.ping_check.return_value = (
            {}, False
        )
        response = self.controller.get()
        self.assertEqual(503, response.status_code)
