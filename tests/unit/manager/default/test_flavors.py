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

import uuid

import mock
from oslo.config import cfg

from poppy.manager.default import driver
from poppy.manager.default import flavors
from poppy.model import flavor
from tests.unit import base


class DefaultManagerFlavorTests(base.TestCase):
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.provider.base.driver.ProviderDriverBase')
    @mock.patch('poppy.dns.base.driver.DNSDriverBase')
    def setUp(self, mock_driver, mock_provider, mock_dns):
        super(DefaultManagerFlavorTests, self).setUp()

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        manager_driver = driver.DefaultManagerDriver(conf,
                                                     mock_driver,
                                                     mock_provider,
                                                     mock_dns)

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

        providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))
        providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))
        providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))

        new_flavor = flavor.Flavor(flavor_id, providers)

        self.fc.add(new_flavor)
        self.fc.storage.add.assert_called_once_with(new_flavor)

    def test_delete(self):
        flavor_id = uuid.uuid1()
        self.fc.delete(flavor_id)

        # ensure the manager calls the storage driver with the appropriate data
        self.fc.storage.delete.assert_called_once_with(flavor_id)
