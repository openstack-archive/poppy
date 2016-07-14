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
from oslo_config import cfg

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
    cfg.StrOpt('consistency_level', default='ONE',
               help='Consistency level of your cassandra query'),
    cfg.StrOpt('migrations_consistency_level', default='LOCAL_QUORUM',
               help='Consistency level of cassandra migration queries'),
    cfg.IntOpt('max_schema_agreement_wait', default=10,
               help='The maximum duration (in seconds) that the driver will'
               ' wait for schema agreement across the cluster.'),
    cfg.DictOpt(
        'replication_strategy',
        default={
            'class': 'SimpleStrategy',
            'replication_factor': '1'
        },
        help='Replication strategy for Cassandra cluster'
    ),
    cfg.StrOpt(
        'migrations_path',
        default='./poppy/storage/cassandra/migrations',
        help='Path to directory containing CQL migration scripts',
    ),
    cfg.BoolOpt('archive_on_delete', default=True,
                help='Archive services on delete?'),
    cfg.BoolOpt('automatic_schema_migration', default=False,
                help='Automatically migrate schema in request ?')
]


class CassandraStorageDriverTests(base.TestCase):

    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        super(CassandraStorageDriverTests, self).setUp()

        cluster_patcher = mock.patch('cassandra.cluster.Cluster')
        self.mock_cluster = cluster_patcher.start()
        self.addCleanup(cluster_patcher.stop)

        conf = cfg.ConfigOpts()
        conf.register_opt(
            cfg.StrOpt(
                'datacenter',
                default='',
                help='datacenter where the C* cluster hosted'))
        conf.register_opts(CASSANDRA_OPTIONS,
                           group=driver.CASSANDRA_GROUP)
        self.conf = conf
        self.cassandra_driver = driver.CassandraStorageDriver(conf)

        migrations_patcher = mock.patch(
            'cdeploy.migrator.Migrator'
        )
        migrations_patcher.start()
        self.addCleanup(migrations_patcher.stop)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEqual(self.cassandra_driver.cassandra_conf['cluster'],
                         ['mock_ip'])
        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace,
                         'mock_poppy')

    def test_ssl_disabled(self):
        cfg = mock.Mock()
        cfg.ssl_enabled = False
        cfg.migrations_consistency_level = 'LOCAL_QUORUM'
        cfg.load_balance_strategy = 'RoundRobinPolicy'

        driver._connection(cfg, None)

        kwargs = self.mock_cluster.call_args[1]
        # ssl_options may or may not be provided to the Cluster constructor
        # depending on the implementation, but if it is provided, ensure it
        # has been set to None
        if 'ssl_options' in kwargs:
            self.assertIsNone(kwargs['ssl_options'])

    def test_ssl_enabled(self):
        cfg = mock.Mock()
        cfg.ssl_enabled = True
        cfg.ssl_ca_certs = '/absolute/path/to/certificate.crt'
        cfg.migrations_consistency_level = 'LOCAL_QUORUM'
        cfg.load_balance_strategy = 'RoundRobinPolicy'

        driver._connection(cfg, None)

        kwargs = self.mock_cluster.call_args[1]
        self.assertTrue('ssl_options' in kwargs)
        ssl_options = kwargs['ssl_options']
        self.assertEqual(cfg.ssl_ca_certs, ssl_options['ca_certs'])
        self.assertEqual(ssl.PROTOCOL_TLSv1, ssl_options['ssl_version'])

    def test_auth_enabled(self):
        cfg = mock.Mock()
        cfg.migrations_consistency_level = 'LOCAL_QUORUM'
        cfg.load_balance_strategy = "RoundRobinPolicy"
        cfg.auth_enabled = True
        cfg.cluster = ['localhost']

        cluster_instance = mock.Mock()
        self.mock_cluster.return_value = cluster_instance

        mock_session = mock.Mock()
        cluster_instance.connect.return_value = mock_session

        session = driver._connection(cfg, "ORD")

        self.assertEqual(mock_session, session)

    def test_create_dc_aware_policy(self):
        cfg = mock.Mock()
        cfg.migrations_consistency_level = 'LOCAL_QUORUM'
        cfg.load_balance_strategy = "DCAwareRoundRobinPolicy"
        cfg.cluster = ['localhost']

        cluster_instance = mock.Mock()
        self.mock_cluster.return_value = cluster_instance

        mock_session = mock.Mock()
        cluster_instance.connect.return_value = mock_session

        session = driver._connection(cfg, "ORD")

        self.assertEqual(mock_session, session)

    def test_consistency_level(self):
        self.assertEqual(self.cassandra_driver.consistency_level,
                         cassandra.ConsistencyLevel.ONE)

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

        cluster_instance = mock.Mock()
        self.mock_cluster.return_value = cluster_instance

        mock_session = mock.Mock()
        cluster_instance.connect.return_value = mock_session

        self.cassandra_driver.delete_namespace('test')
        self.assertTrue(mock_session.execute.called)
        mock_session.execute.assert_called_with('DROP KEYSPACE test')

    def test_is_alive_negative(self):
        """No connection test for checking the health of Cassandra."""

        self.cassandra_driver.database.execute.side_effect = (
            Exception("Mock -- DB execute() failed!")
        )
        self.cassandra_driver.session = None
        self.assertFalse(self.cassandra_driver.is_alive())

    def test_is_alive_positive(self):
        """No connection test for checking the health of Cassandra."""

        self.cassandra_driver.session = None
        self.assertTrue(self.cassandra_driver.is_alive())

    def test_is_alive_with_exception(self):
        """Broken connection test for checking the health of Cassandra."""

        self.cassandra_driver.session = None
        self.cassandra_driver.connect = mock.Mock()
        self.cassandra_driver.session = mock.Mock(is_shutdown=False)
        self.cassandra_driver.session.execute = mock.Mock(
            side_effect=Exception('Cassandra Not Available'))
        self.assertTrue(self.cassandra_driver.database is not None)
        self.assertFalse(self.cassandra_driver.is_alive())

    def test_is_alive(self):
        """Happy path test for checking the health of Cassandra."""

        self.cassandra_driver.session = None
        self.cassandra_driver.connect = mock.Mock()
        self.assertTrue(self.cassandra_driver.database is None)
        self.assertFalse(self.cassandra_driver.is_alive())

    @mock.patch('cassandra.cluster.Cluster')
    def test_connection(self, mock_cluster):
        self.cassandra_driver.connection()
        mock_cluster.return_value.connect.assert_called_with()

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
        self.assertIsNone(self.cassandra_driver.session)

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

    def test_database(self):
        self.cassandra_driver.database
        self.mock_cluster.return_value.connect.assert_called_with()

    def test_connection_create_key_space(self):
        self.conf.default_consistency_level = 'ALL'

        cluster_instance = mock.Mock()
        self.mock_cluster.return_value = cluster_instance

        mock_session = mock.Mock()
        mock_session.set_keyspace.side_effect = (
            cassandra.InvalidRequest
        )
        cluster_instance.connect.return_value = mock_session

        self.assertRaises(
            cassandra.InvalidRequest,
            driver._connection,
            self.conf[driver.CASSANDRA_GROUP],
            'ORD',
            keyspace='keyspace'
        )

    def test_change_config_group(self):
        old_cassandra_conf = self.cassandra_driver.cassandra_conf
        new_opts = [
            cfg.ListOpt('test', default='test')
        ]
        self.cassandra_driver.change_config_group(
            new_opts, 'test_group'
        )

        self.assertFalse(
            old_cassandra_conf ==
            self.cassandra_driver.cassandra_conf
        )

    def test_close_connection_no_lock(self):
        self.cassandra_driver.connect()
        with mock.patch.object(
                self.cassandra_driver, 'lock'
        ) as mock_lock:
            mock_lock.acquire.return_value = False

            self.cassandra_driver.close_connection()

            self.assertFalse(mock_lock.return_value.release.called)
