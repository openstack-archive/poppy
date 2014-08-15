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

import cassandra
import ddt
import mock
from oslo.config import cfg

from poppy.storage.cassandra import driver
from poppy.storage.cassandra import flavors
from poppy.transport.pecan.models.request import flavor
from tests.unit import base


@ddt.ddt
class CassandraStorageFlavorsTests(base.TestCase):

    def setUp(self):
        super(CassandraStorageFlavorsTests, self).setUp()

        self.flavor_id = uuid.uuid1()

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.CassandraStorageDriver(conf)

        # stubbed cassandra driver
        self.fc = flavors.FlavorsController(cassandra_driver)

    @ddt.file_data('data_get_flavor.json')
    @mock.patch.object(flavors.FlavorsController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_flavor(self, value, mock_session, mock_execute):

        # mock the response from cassandra
        mock_execute.execute.return_value = value

        actual_response = self.fc.get(value[0]['flavor_id'])

        self.assertEqual(actual_response.flavor_id, value[0]['flavor_id'])
        self.assertEqual(
            len(actual_response.providers), len(value[0]['providers']))

    @ddt.file_data('../data/data_create_flavor.json')
    @mock.patch.object(flavors.FlavorsController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_add_flavor(self, value, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = value

        new_flavor = flavor.load_from_json(value)

        actual_response = self.fc.add(new_flavor)

        self.assertEqual(actual_response, None)

    @ddt.file_data('data_list_flavors.json')
    @mock.patch.object(flavors.FlavorsController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_list_flavors(self, value, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = value

        actual_response = self.fc.list()

        # confirm the correct number of results are returned
        self.assertEqual(len(actual_response), len(value))

        # confirm the flavor id is returned for each expectation
        i = 0
        for r in actual_response:
            self.assertEqual(r.flavor_id, value[i]['flavor_id'])
            i = i + 1

    @mock.patch.object(flavors.FlavorsController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_delete_flavor(self, mock_session, mock_execute):
        actual_response = self.fc.delete(self.flavor_id)

        self.assertEqual(actual_response, None)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_session(self, mock_flavor_database):
        session = self.fc.session
        self.assertNotEqual(session, None)
