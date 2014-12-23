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

import ssl

import cassandra
import mock
from oslo.config import cfg

from poppy.storage.cassandra import driver
from poppy.storage.cassandra import flavors
from poppy.storage.cassandra import services
from tests.unit import base


CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.IntOpt('port', default=9042, help='Cassandra cluster port'),
    cfg.StrOpt('keyspace', default='mock_poppy',
               help='Keyspace for all queries made in session'),
    cfg.BoolOpt('ssl_enabled', default=False,
                help='Communicate with Cassandra over SSL?'),
    cfg.StrOpt('ssl_ca_certs', default='',
               help='Absolute path to the appropriate .crt file'),
    cfg.BoolOpt('auth_enabled', default=False,
                help='Does Cassandra have authentication enabled?'),
    cfg.StrOpt('username', default='', help='Cassandra username'),
    cfg.StrOpt('password', default='', help='Cassandra password'),
    cfg.StrOpt('load_balance_strategy', default='RoundRobinPolicy',
               help='Load balancing strategy for connecting to cluster nodes'),
    cfg.DictOpt(
        'replication_strategy',
        default={
            'class': 'SimpleStrategy',
            'replication_factor': '1'
        },
        help='Replication strategy for Cassandra cluster'
    ),
    cfg.BoolOpt('archive_on_delete', default=True,
                help='Archive services on delete?'),
]


class CassandraStorageDriverTests(base.TestCase):

    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        super(CassandraStorageDriverTests, self).setUp()

        conf = cfg.ConfigOpts()
        conf.register_opt(
            cfg.StrOpt(
                'datacenter',
                default='',
                help='datacenter where the C* cluster hosted'))
        conf.register_opts(CASSANDRA_OPTIONS,
                           group=driver.CASSANDRA_GROUP)
        self.cassandra_driver = driver.CassandraStorageDriver(conf)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEqual(self.cassandra_driver.cassandra_conf['cluster'],
                         ['mock_ip'])
        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace,
                         'mock_poppy')

    def test_ssl_disabled(self):
        cfg = mock.Mock()
        cfg.ssl_enabled = False

        cfg.load_balance_strategy = 'RoundRobinPolicy'

        with mock.patch('cassandra.cluster.Cluster') as mock_cluster:
            driver._connection(cfg, None)

            kwargs = mock_cluster.call_args[1]
            # ssl_options may or may not be provided to the Cluster constructor
            # depending on the implementation, but if it is provided, ensure it
            # has been set to None
            if 'ssl_options' in kwargs:
                self.assertIsNone(kwargs['ssl_options'])

    def test_ssl_enabled(self):
        cfg = mock.Mock()
        cfg.ssl_enabled = True
        cfg.ssl_ca_certs = '/absolute/path/to/certificate.crt'

        cfg.load_balance_strategy = 'RoundRobinPolicy'

        with mock.patch('cassandra.cluster.Cluster') as mock_cluster:
            driver._connection(cfg, None)

            kwargs = mock_cluster.call_args[1]
            self.assertTrue('ssl_options' in kwargs)
            ssl_options = kwargs['ssl_options']
            self.assertEqual(cfg.ssl_ca_certs, ssl_options['ca_certs'])
            self.assertEqual(ssl.PROTOCOL_TLSv1, ssl_options['ssl_version'])

    def test_auth_enabled(self):
        cfg = mock.Mock()
        cfg.load_balance_strategy = "RoundRobinPolicy"
        cfg.auth_enabled = True
        cfg.cluster = ['localhost']

        with mock.patch("cassandra.cluster.Cluster") as mock_cluster:
            cluster_instance = mock.Mock()
            mock_cluster.return_value = cluster_instance

            mock_session = mock.Mock()
            cluster_instance.connect.return_value = mock_session

            session = driver._connection(cfg, "ORD")

            self.assertEqual(mock_session, session)

    def test_create_dc_aware_policy(self):
        cfg = mock.Mock()
        cfg.load_balance_strategy = "DCAwareRoundRobinPolicy"
        cfg.cluster = ['localhost']

        with mock.patch("cassandra.cluster.Cluster") as mock_cluster:
            cluster_instance = mock.Mock()
            mock_cluster.return_value = cluster_instance

            mock_session = mock.Mock()
            cluster_instance.connect.return_value = mock_session

            session = driver._connection(cfg, "ORD")

            self.assertEqual(mock_session, session)

    def test_storage_name(self):
        self.assertEqual('Cassandra', self.cassandra_driver.storage_name)

    def test_change_namespace(self):
        '''Test switching keyspaces.

        Since there is no database communication during this action so, there
        is no need to mock any of the database calls.  The initial keyspace
        is "phoenix".
        '''

        self.assertIsNotNone(self.cassandra_driver)
        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace,
                         'mock_poppy')

        self.cassandra_driver.change_namespace('test')

        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace, 'test')

    def test_delete_namespace(self):
        '''Test deleting a keyspace.

        This action requires database communication, so all db interaction is
        mocked.
        '''

        with mock.patch('cassandra.cluster.Cluster') as mock_cluster:
            cluster_instance = mock.Mock()
            mock_cluster.return_value = cluster_instance

            mock_session = mock.Mock()
            cluster_instance.connect.return_value = mock_session

            self.cassandra_driver.delete_namespace('test')
            self.assertTrue(mock_session.execute.called)
            mock_session.execute.assert_called_with('DROP KEYSPACE test')

    # def test_is_alive_no_connection(self):
    #     """No connection test for checking the health of Cassandra."""

    #     self.cassandra_driver.session = None
    #     self.assertFalse(self.cassandra_driver.is_alive())

    # def test_is_alive_with_exception(self):
    #     """Broken connection test for checking the health of Cassandra."""

    #     self.cassandra_driver.session = None
    #     self.cassandra_driver.connect = mock.Mock()
    #     self.cassandra_driver.session = mock.Mock(is_shutdown=False)
    #     self.cassandra_driver.session.execute = mock.Mock(
    #         side_effect=Exception('Cassandra Not Available'))
    #     self.assertTrue(self.cassandra_driver.database is not None)
    #     self.assertFalse(self.cassandra_driver.is_alive())

    # def test_is_alive(self):
    #     """Happy path test for checking the health of Cassandra."""

    #     self.cassandra_driver.session = None
    #     self.cassandra_driver.connect = mock.Mock()
    #     self.assertTrue(self.cassandra_driver.database is None)
    #     self.assertFalse(self.cassandra_driver.is_alive())

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_connection(self, mock_cluster):
        self.cassandra_driver.connection()
        mock_cluster.assert_called_with()

    def test_connect(self):
        self.cassandra_driver.session = None
        self.cassandra_driver.connect = mock.Mock()
        self.cassandra_driver.database
        self.cassandra_driver.connect.assert_called_once_with()
        # reset session to not None value
        self.cassandra_driver.session = mock.Mock(is_shutdown=False)
        # 2nd time should get a not-none session
        self.assertTrue(self.cassandra_driver.database is not None)

    def test_close_connection(self):
        self.cassandra_driver.session = mock.Mock()
        self.cassandra_driver.close_connection()

        self.cassandra_driver.session.cluster.shutdown.assert_called_once_with(
        )
        self.cassandra_driver.session.shutdown.assert_called_once_with(
        )

    def test_service_controller(self):
        sc = self.cassandra_driver.services_controller

        self.assertEqual(
            isinstance(sc, services.ServicesController),
            True)

    def test_flavor_controller(self):
        sc = self.cassandra_driver.flavors_controller

        self.assertEqual(
            isinstance(sc, flavors.FlavorsController),
            True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_database(self, mock_cluster):
        self.cassandra_driver.database
        mock_cluster.assert_called_with()
