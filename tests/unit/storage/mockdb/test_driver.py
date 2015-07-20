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

from oslo_config import cfg

from poppy.storage.mockdb import driver
from tests.unit import base


class MockDBStorageDriverTests(base.TestCase):

    def setUp(self):
        super(MockDBStorageDriverTests, self).setUp()

        self.mockdb_driver = driver.MockDBStorageDriver(cfg.CONF)

    def test_is_alive(self):
        self.assertTrue(self.mockdb_driver.is_alive())

    def test_database(self):
        self.assertTrue(self.mockdb_driver.database is None)

    def test_connect(self):
        self.assertTrue(self.mockdb_driver.connect() == "")

    def test_connection(self):
        self.assertTrue(self.mockdb_driver.connection is None)

    def test_close_connection(self):
        self.assertTrue(self.mockdb_driver.close_connection() is None)

    def test_services_controller(self):
        self.assertTrue(self.mockdb_driver.services_controller.session is None)

    def test_flavors_controller(self):
        self.assertTrue(self.mockdb_driver.flavors_controller.session is None)
