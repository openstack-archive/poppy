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

import ddt

from poppy.common import util
from poppy.transport.pecan.models.response import health
from tests.unit import base


class TestDNSModel(base.TestCase):

    def setUp(self):
        super(TestDNSModel, self).setUp()

    def test_dns_is_alive(self):
        dns_model = health.DNSModel(True)
        self.assertEqual('true', dns_model['online'])

    def test_dns_is_not_alive(self):
        dns_model = health.DNSModel(False)
        self.assertEqual('false', dns_model['online'])


class TestDistributedTaskModel(base.TestCase):

    def setUp(self):
        super(TestDistributedTaskModel, self).setUp()

    def test_distributed_task_is_alive(self):
        distributed_task_model = health.DistributedTaskModel(True)
        self.assertEqual('true', distributed_task_model['online'])

    def test_distributed_task_is_not_alive(self):
        distributed_task_model = health.DistributedTaskModel(False)
        self.assertEqual('false', distributed_task_model['online'])


class TestStorageModel(base.TestCase):

    def setUp(self):
        super(TestStorageModel, self).setUp()

    def test_storage_is_alive(self):
        storage_model = health.StorageModel(True)
        self.assertEqual('true', storage_model['online'])

    def test_storage_is_not_alive(self):
        storage_model = health.StorageModel(False)
        self.assertEqual('false', storage_model['online'])


class TestProviderModel(base.TestCase):

    def setUp(self):
        super(TestProviderModel, self).setUp()

    def test_provider_is_alive(self):
        provider_model = health.ProviderModel(True)
        self.assertEqual('true', provider_model['online'])

    def test_provider_is_not_alive(self):
        provider_model = health.ProviderModel(False)
        self.assertEqual('false', provider_model['online'])


@ddt.ddt
class TestHealthModel(base.TestCase):

    def setUp(self):
        super(TestHealthModel, self).setUp()
        self.mock_controller = util.dict2obj(
            {'base_url': 'https://www.poppycdn.io/'})

    @ddt.file_data('health_map.json')
    def test_health(self, health_map):
        health_model = health.HealthModel(self.mock_controller, health_map)
        storage_name = health_map['storage']['storage_name']
        self.assertEqual('true',
                         health_model['storage'][storage_name]['online'])
        dns_name = health_map['dns']['dns_name']
        self.assertEqual('true',
                         health_model['dns'][dns_name]['online'])
        distributed_task_name = \
            health_map['distributed_task']['distributed_task_name']
        status = \
            health_model['distributed_task'][distributed_task_name]['online']
        self.assertEqual('true', status)

    @ddt.file_data('health_map_dns_not_available.json')
    def test_health_dns_not_available(self, health_map):
        health_model = health.HealthModel(self.mock_controller, health_map)
        dns_name = health_map['dns']['dns_name']
        self.assertEqual('false',
                         health_model['dns'][dns_name]['online'])

    @ddt.file_data('health_map_storage_not_available.json')
    def test_health_storage_not_available(self, health_map):
        health_model = health.HealthModel(self.mock_controller, health_map)
        storage_name = health_map['storage']['storage_name']
        self.assertEqual('false',
                         health_model['storage'][storage_name]['online'])

    @ddt.file_data('health_map_provider_not_available.json')
    def test_health_provider_not_available(self, health_map):
        health_model = health.HealthModel(self.mock_controller, health_map)
        providers = health_map['providers']

        for provider in providers:
            provider_name = provider['provider_name']
            provider_is_alive = provider['is_alive']
            provider_model = health_model['providers'][provider_name]
            if provider_is_alive:
                self.assertEqual('true', provider_model['online'])
            else:
                self.assertEqual('false', provider_model['online'])

    @ddt.file_data('health_map_distributed_task_not_available.json')
    def test_health_distributed_task_not_available(self, health_map):
        health_model = health.HealthModel(self.mock_controller, health_map)
        distributed_task = health_map['distributed_task']
        distributed_task_name = distributed_task['distributed_task_name']
        status = health_model['distributed_task'][distributed_task_name]
        self.assertEqual('false', status['online'])
