import cassandra

from cdn.storage.cassandra import driver
from mock import patch
from unittest import TestCase


class CassandraOpts():
    @property
    def cluster(self):
        return ['localhost']

    @property
    def keyspace(self):
        return 'cdn'


class CassandraStorageServiceTests(TestCase):

    @patch.object(cassandra.cluster.Cluster, 'connect')
    def test_connection_keyspace(self, mock_cluster):
        conf = CassandraOpts()
        driver._connection(conf)

        # assert we connect to cassandra with the correct keyspace
        mock_cluster.assert_called_with('cdn')
