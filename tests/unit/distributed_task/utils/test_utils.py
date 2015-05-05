# Copyright (c) 2015 Rackspace, Inc.
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

"""Unittests for TaskFlow distributed_task driver implementation."""

from poppy.distributed_task.utils import memoized_controllers
from tests.unit import base


class TestMemoizeUtils(base.TestCase):

    def setUp(self):
        super(TestMemoizeUtils, self).setUp()

    def test_memoization_service_controller(self):
        service_controller_first = \
            memoized_controllers.task_controllers('poppy')
        service_controller_cached = \
            memoized_controllers.task_controllers('poppy')

        self.assertEqual(id(service_controller_first),
                         id(service_controller_cached))

    def test_memoization_storage_controller(self):
        service_controller_first, storage_controller_first = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_controller_cached, storage_controller_cached = \
            memoized_controllers.task_controllers('poppy', 'storage')

        self.assertEqual(id(service_controller_first),
                         id(service_controller_cached))
        self.assertEqual(id(storage_controller_first),
                         id(storage_controller_cached))

    def test_memoization_dns_controller(self):
        service_controller_first, dns_controller_first = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_controller_cached, dns_controller_cached = \
            memoized_controllers.task_controllers('poppy', 'storage')

        self.assertEqual(id(service_controller_first),
                         id(service_controller_cached))
        self.assertEqual(id(dns_controller_first),
                         id(dns_controller_cached))
