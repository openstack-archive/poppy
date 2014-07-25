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
import unittest

from oslo.config import cfg

from cdn.storage.cassandra import driver
from cdn.storage.cassandra import services


CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='mock_cdn',
               help='Keyspace for all queries made in session'),
]


class CassandraStorageServiceTests(unittest.TestCase):
    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        conf = cfg.ConfigOpts()
        self.cassandra_driver = driver.CassandraStorageDriver(conf)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEquals(self.cassandra_driver.cassandra_conf['cluster'],
                          ['mock_ip'])
        self.assertEquals(self.cassandra_driver.cassandra_conf.keyspace,
                          'mock_cdn')

    def test_is_alive(self):
        self.assertEquals(self.cassandra_driver.is_alive(), True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_connection(self, mock_cluster):
        self.cassandra_driver.connection()
        mock_cluster.assert_called_with('mock_cdn')

    def test_service_controller(self):
        sc = self.cassandra_driver.service_controller

        self.assertEquals(
            isinstance(sc, services.ServicesController),
            True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_service_database(self, mock_cluster):
        self.cassandra_driver.service_database
        mock_cluster.assert_called_with('mock_cdn')
