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

import cassandra
import mock
from oslo.config import cfg

from poppy.storage.cassandra import driver
from poppy.storage.cassandra import services
from tests.unit import base


CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='mock_poppy',
               help='Keyspace for all queries made in session'),
]


class CassandraStorageServiceTests(base.TestCase):

    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        super(CassandraStorageServiceTests, self).setUp()

        conf = cfg.ConfigOpts()
        self.cassandra_driver = driver.CassandraStorageDriver(conf)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEqual(self.cassandra_driver.cassandra_conf['cluster'],
                         ['mock_ip'])
        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace,
                         'mock_poppy')

    def test_is_alive(self):
        self.assertEqual(self.cassandra_driver.is_alive(), True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_connection(self, mock_cluster):
        self.cassandra_driver.connection()
        mock_cluster.assert_called_with('mock_poppy')

    def test_service_controller(self):
        sc = self.cassandra_driver.service_controller

        self.assertEqual(
            isinstance(sc, services.ServicesController),
            True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_service_database(self, mock_cluster):
        self.cassandra_driver.service_database
        mock_cluster.assert_called_with('mock_poppy')
