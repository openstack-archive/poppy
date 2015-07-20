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

import ddt
import mock
from oslo_config import cfg

from poppy.storage.mockdb import driver
from poppy.storage.mockdb import flavors
from poppy.transport.pecan.models.request import flavor
from tests.unit import base


@ddt.ddt
class MockDBStorageFlavorsTests(base.TestCase):

    def setUp(self):
        super(MockDBStorageFlavorsTests, self).setUp()

        self.flavor_id = uuid.uuid1()

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        mockdb_driver = driver.MockDBStorageDriver(conf)

        # stubbed driver
        self.fc = flavors.FlavorsController(mockdb_driver)

    @mock.patch.object(flavors.FlavorsController, 'session')
    def test_get_flavor(self, mock_session):

        actual_response = self.fc.get(self.flavor_id)

        self.assertEqual(actual_response.flavor_id, "standard")

    @mock.patch.object(flavors.FlavorsController, 'session')
    @ddt.file_data('../data/data_create_flavor.json')
    def test_add_flavor(self, mock_session, value):
        new_flavor = flavor.load_from_json(value)

        actual_response = self.fc.add(new_flavor)

        self.assertEqual(actual_response, None)

    @mock.patch.object(flavors.FlavorsController, 'session')
    def test_list_flavors(self, mock_session):
        actual_response = self.fc.list()

        # confirm the correct number of results are returned
        self.assertEqual(len(actual_response), 1)
        self.assertEqual(actual_response[0].flavor_id, "standard")

    @mock.patch.object(flavors.FlavorsController, 'session')
    def test_delete_flavor(self, mock_session):
        actual_response = self.fc.delete(self.flavor_id)

        self.assertEqual(actual_response, None)

    def test_session(self):
        session = self.fc.session
        self.assertEqual(session, None)
