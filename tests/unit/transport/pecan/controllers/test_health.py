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
from poppy.transport.pecan.models.response import health
from tests.unit.transport.pecan.controllers import base


class HealthControllerTests(base.BasePecanControllerUnitTest):

    def setUp(self):
        super(HealthControllerTests, self).setUp(
            poppy.transport.pecan.controllers.v1.admin
        )

        self.controller = controllers.v1.health.HealthController(self.driver)
        self.manager = self.driver.manager
        self.response.status = 0

    def test_health_not_alive(self):
        self.controller.base_url = 'base_url'
        self.manager.health_controller.health.return_value = (
            False, {
                'dns': {
                    'is_alive': True,
                    'dns_name': 'example_cloud_dns'
                },
                'storage': {
                    'is_alive': True,
                    'storage_name': 'example_storage'
                },
                'distributed_task': {
                    'is_alive': True,
                    'distributed_task_name': 'example_distributed_task'
                },
                'providers': [
                    {
                        'is_alive': True,
                        'provider_name': 'example_provider'
                    }
                ],
            }
        )
        response = self.controller.get()
        self.assertIsInstance(response, health.HealthModel)
        self.assertEqual(503, self.response.status)
