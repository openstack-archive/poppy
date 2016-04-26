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

"""Cassandra storage driver implementation."""

import copy
import multiprocessing
import os
import ssl

import cassandra
from cassandra import auth
from cassandra import cluster
from cassandra import policies
from cassandra import query
from cdeploy import migrator
from oslo_config import cfg
from oslo_log import log

from poppy.storage import base
from poppy.storage.cassandra import controllers


LOG = log.getLogger(__name__)

CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default=['127.0.0.1'],
                help='Cassandra cluster contact points'),
    cfg.IntOpt('port', default=9042, help='Cassandra cluster port'),
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
    cfg.StrOpt('keyspace', default='poppy',
               help='Keyspace for all queries made in session'),
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
        default=os.path.join(os.path.dirname(__file__), 'migrations'),
        help='Path to directory containing CQL migration scripts',
    ),
    cfg.BoolOpt('archive_on_delete', default=True,
                help='Archive services on delete?'),
    cfg.BoolOpt('automatic_schema_migration', default=False,
                help='Automatically migrate schema in request ?')
]

CASSANDRA_GROUP = 'drivers:storage:cassandra'


def _connection(conf, datacenter, keyspace=None):
    """connection.

    :param datacenter
    :returns session
    """
    ssl_options = None
    if conf.ssl_enabled:
        ssl_options = {
            'ca_certs': conf.ssl_ca_certs,
            'ssl_version': ssl.PROTOCOL_TLSv1
        }

    auth_provider = None
    if conf.auth_enabled:
        auth_provider = auth.PlainTextAuthProvider(
            username=conf.username,
            password=conf.password
        )

    load_balancing_policy_class = getattr(policies, conf.load_balance_strategy)
    if load_balancing_policy_class is policies.DCAwareRoundRobinPolicy:
        load_balancing_policy = load_balancing_policy_class(datacenter)
    else:
        load_balancing_policy = load_balancing_policy_class()

    cluster_connection = cluster.Cluster(
        conf.cluster,
        auth_provider=auth_provider,
        load_balancing_policy=load_balancing_policy,
        port=conf.port,
        ssl_options=ssl_options,
        max_schema_agreement_wait=conf.max_schema_agreement_wait
    )

    session = cluster_connection.connect()
    if not keyspace:
        keyspace = conf.keyspace
    try:
        session.set_keyspace(keyspace)
    except cassandra.InvalidRequest:
        _create_keyspace(session, keyspace, conf.replication_strategy)

    if conf.automatic_schema_migration:
        migration_session = copy.copy(session)
        migration_session.default_consistency_level = \
            getattr(cassandra.ConsistencyLevel,
                    conf.migrations_consistency_level)
        _run_migrations(conf.migrations_path, migration_session)

    session.row_factory = query.dict_factory

    return session


def _create_keyspace(session, keyspace, replication_strategy):
    """create_keyspace.

    :param keyspace
    :param replication_strategy
    """
    LOG.debug('Creating keyspace: ' + keyspace)

    # replication factor will come in as a string with quotes already
    session.execute(
        "CREATE KEYSPACE " + keyspace + " " +
        "WITH REPLICATION = " + str(replication_strategy) + ";"
    )
    session.set_keyspace(keyspace)


def _run_migrations(migrations_path, session):
    LOG.debug('Running schema migration(s)')

    schema_migrator = migrator.Migrator(migrations_path, session)
    schema_migrator.run_migrations()


class CassandraStorageDriver(base.Driver):
    """Cassandra Storage Driver."""

    def __init__(self, conf):
        super(CassandraStorageDriver, self).__init__(conf)

        self.conf = conf
        conf.register_opts(CASSANDRA_OPTIONS, group=CASSANDRA_GROUP)
        self.cassandra_conf = conf[CASSANDRA_GROUP]
        self.datacenter = conf.datacenter
        self.consistency_level = getattr(
            cassandra.ConsistencyLevel,
            conf[CASSANDRA_GROUP].consistency_level)
        self.session = None
        self.archive_on_delete = self.cassandra_conf.archive_on_delete
        self.lock = multiprocessing.Lock()

    def change_config_group(self, options, group):
        self.conf.register_opts(options, group=group)
        self.cassandra_conf = self.conf[group]

    def change_namespace(self, namespace):
        """change_namespace.

        :param namespace
        """
        self.cassandra_conf.keyspace = namespace

    def delete_namespace(self, namespace):
        """delete_namespace.

        :param namespace
        """
        self.connection.execute('DROP KEYSPACE ' + namespace)

    def is_alive(self):
        """Health check for Cassandra."""

        try:
            self.database.execute(
                "SELECT cluster_name, data_center FROM system.local;")
        except Exception as ex:
            LOG.exception("Cassandra storage health check failed: {0}".format(
                str(ex))
            )
            return False
        return True

    @property
    def storage_name(self):
        """storage name.

        :returns 'Cassandra'
        """
        return 'Cassandra'

    @property
    def connection(self):
        """Cassandra connection instance."""
        return _connection(self.cassandra_conf, self.datacenter)

    @property
    def certificates_controller(self):
        """certificates_controller.

        :returns certificates controller
        """
        return controllers.CertificatesController(self)

    @property
    def flavors_controller(self):
        """flavors_controller.

        :returns flavor controller
        """
        return controllers.FlavorsController(self)

    @property
    def services_controller(self):
        """services_controller.

        :returns service controller
        """
        return controllers.ServicesController(self)

    @property
    def database(self):
        """database.

        :returns session
        """
        # if the session has been shutdown, reopen a session
        # Add a time out when acquiring lock to avoid deadlock
        # typically the lock acquiring will not hit timeout,
        # in the case of massive database connection in a short
        # amount of time, timeout can help avoid deadlock and
        # can keep system running fine
        # see https://docs.python.org/2/library/multiprocessing.html#
        # synchronization-primitives for more details
        lock_success = False
        try:
            if self.session is None or self.session.is_shutdown:
                # only require lock when the session is closed
                lock_success = self.lock.acquire(block=True, timeout=10)
                self.connect()
        finally:
            if lock_success:
                self.lock.release()
        return self.session

    def connect(self):
        """connect.

        :returns connection
        """
        self.session = _connection(self.cassandra_conf, self.datacenter)

    def close_connection(self):
        """close_connection."""
        lock_success = False
        try:
            lock_success = self.lock.acquire(block=True, timeout=10)
            self.session.cluster.shutdown()
            self.session.shutdown()
            self.session = None
        finally:
            if lock_success:
                self.lock.release()
