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

import multiprocessing
import ssl

import cassandra
from cassandra import auth
from cassandra import cluster
from cassandra import policies
from cassandra import query
from oslo.config import cfg

from poppy.openstack.common import log as logging
from poppy.storage import base
from poppy.storage.cassandra import controllers
from poppy.storage.cassandra import schema


LOG = logging.getLogger(__name__)

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
    cfg.BoolOpt('archive_on_delete', default=True,
                help='Archive services on delete?'),
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
        ssl_options=ssl_options
    )

    session = cluster_connection.connect()
    if not keyspace:
        keyspace = conf.keyspace
    try:
        session.set_keyspace(keyspace)
    except cassandra.InvalidRequest:
        _create_keyspace(session, keyspace, conf.replication_strategy)

    session.row_factory = query.dict_factory

    return session


def _create_keyspace(session, keyspace, replication_strategy):
    """create_keyspace.

    :param keyspace
    :param replication_strategy
    """
    # replication factor will come in as a string with quotes already
    session.execute(
        "CREATE KEYSPACE " + keyspace + " " +
        "WITH REPLICATION = " + str(replication_strategy) + ";"
    )
    session.set_keyspace(keyspace)

    for statement in schema.schema_statements:
        session.execute(statement)

    LOG.debug('Creating keyspace: ' + keyspace)


class CassandraStorageDriver(base.Driver):
    """Cassandra Storage Driver."""

    def __init__(self, conf):
        super(CassandraStorageDriver, self).__init__(conf)
        conf.register_opts(CASSANDRA_OPTIONS, group=CASSANDRA_GROUP)
        self.cassandra_conf = conf[CASSANDRA_GROUP]
        self.datacenter = conf.datacenter
        self.session = None
        self.archive_on_delete = self.cassandra_conf.archive_on_delete
        self.lock = multiprocessing.Lock()

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
            session = _connection(self.cassandra_conf,
                                  self.datacenter,
                                  keyspace='system')
            session.execute("SELECT cluster_name, data_center FROM local;")
            session.shutdown()
        except Exception:
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
    def services_controller(self):
        """services_controller.

        :returns service controller
        """
        return controllers.ServicesController(self)

    @property
    def flavors_controller(self):
        """flavors_controller.

        :returns flavor controller
        """
        return controllers.FlavorsController(self)

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
        finally:
            if lock_success:
                self.lock.release()
