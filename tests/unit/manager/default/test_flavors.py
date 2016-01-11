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

import os
import uuid

import mock
from oslo_config import cfg

from poppy.manager.default import driver
from poppy.manager.default import flavors
from poppy.model import flavor
from tests.unit import base


class DefaultManagerFlavorTests(base.TestCase):
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.provider.base.driver.ProviderDriverBase')
    @mock.patch('poppy.dns.base.driver.DNSDriverBase')
    @mock.patch('poppy.distributed_task.base.driver.DistributedTaskDriverBase')
    @mock.patch('poppy.notification.base.driver.NotificationDriverBase')
    @mock.patch('poppy.metrics.base.driver.MetricsDriverBase')
    def setUp(self, mock_driver, mock_provider, mock_dns,
              mock_distributed_task, mock_notification, mock_metrics):
        super(DefaultManagerFlavorTests, self).setUp()

        # create mocked config and driver
        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))))
        conf_path = os.path.join(tests_path, 'etc', 'default_functional.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])

        manager_driver = driver.DefaultManagerDriver(cfg.CONF,
                                                     mock_driver,
                                                     mock_provider,
                                                     mock_dns,
                                                     mock_distributed_task,
                                                     mock_notification,
                                                     mock_metrics)

        # stubbed driver
        self.fc = flavors.DefaultFlavorsController(manager_driver)

    def test_list(self):

        results = self.fc.list()

        # ensure the manager calls the storage driver with the appropriate data
        self.fc.storage.list.assert_called_once()

        # and that a list of flavors objects are returned
        [self.assertIsInstance(x, flavor.Flavor) for x in results]

    def test_get(self):
        flavor_id = uuid.uuid1()
        self.fc.get(flavor_id)

        # ensure the manager calls the storage driver with the appropriate data
        self.fc.storage.get.assert_called_once_with(flavor_id)

    def test_add(self):
        flavor_id = uuid.uuid1()
        providers = []

        providers.append(flavor.Provider("mock", uuid.uuid1()))
        providers.append(flavor.Provider("mock", uuid.uuid1()))
        providers.append(flavor.Provider("mock", uuid.uuid1()))

        new_flavor = flavor.Flavor(flavor_id, providers)

        self.fc.add(new_flavor)
        self.fc.storage.add.assert_called_once_with(new_flavor)

    def test_delete(self):
        flavor_id = uuid.uuid1()
        self.fc.delete(flavor_id)

        # ensure the manager calls the storage driver with the appropriate data
        self.fc.storage.delete.assert_called_once_with(flavor_id)
