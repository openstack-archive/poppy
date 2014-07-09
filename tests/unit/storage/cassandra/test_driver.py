import cassandra

from cdn.storage.cassandra import driver
from cdn.storage.cassandra import services
from mock import patch
from oslo.config import cfg
from unittest import TestCase

CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='mock_cdn',
               help='Keyspace for all queries made in session'),
]


class CassandraStorageServiceTests(TestCase):

    @patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def test_storage_driver(self):
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.StorageDriver(conf, None)

        # assert that the configs are set up based on what was passed in
        self.assertEquals(cassandra_driver.cassandra_conf['cluster'],
                          ['mock_ip'])
        self.assertEquals(cassandra_driver.cassandra_conf.keyspace,
                          'mock_cdn')

    def test_is_alive(self):
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.StorageDriver(conf, None)

        self.assertEquals(cassandra_driver.is_alive(), True)

    @patch.object(cassandra.cluster.Cluster, 'connect')
    @patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def test_connection(self, mock_cluster):
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.StorageDriver(conf, None)

        cassandra_driver.connection()
        mock_cluster.assert_called_with('mock_cdn')

    def test_service_controller(self):
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.StorageDriver(conf, None)

        sc = cassandra_driver.service_controller

        self.assertIsInstance(sc, services.ServicesController)

    @patch.object(cassandra.cluster.Cluster, 'connect')
    @patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def test_service_database(self, mock_cluster):
        conf = cfg.ConfigOpts()
        cassandra_driver = driver.StorageDriver(conf, None)

        cassandra_driver.service_database
        mock_cluster.assert_called_with('mock_cdn')
