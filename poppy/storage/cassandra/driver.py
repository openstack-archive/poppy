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
]

CASSANDRA_GROUP = 'drivers:storage:cassandra'


def _connection(conf, datacenter):
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

    try:
        session.set_keyspace(conf.keyspace)
    except cassandra.InvalidRequest:
        _create_keyspace(session, conf.keyspace, conf.replication_strategy)

    session.row_factory = query.dict_factory

    return session


def _create_keyspace(session, keyspace, replication_strategy):
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

    def __init__(self, conf):
        super(CassandraStorageDriver, self).__init__(conf)
        conf.register_opts(CASSANDRA_OPTIONS, group=CASSANDRA_GROUP)
        self.cassandra_conf = conf[CASSANDRA_GROUP]
        self.datacenter = conf.datacenter
        self.session = None
        self.lock = multiprocessing.Lock()

    def change_namespace(self, namespace):
        self.cassandra_conf.keyspace = namespace

    def delete_namespace(self, namespace):
        self.connection.execute('DROP KEYSPACE ' + namespace)

    def is_alive(self):
        return True

    @property
    def storage_name(self):
        """For name."""
        return 'Cassandra'

    @property
    def connection(self):
        """Cassandra connection instance."""
        return _connection(self.cassandra_conf, self.datacenter)

    @property
    def services_controller(self):
        return controllers.ServicesController(self)

    @property
    def flavors_controller(self):
        return controllers.FlavorsController(self)

    @property
    def database(self):
        # if the session has been shutdown, reopen a session
        self.lock.acquire()
        if self.session is None or self.session.is_shutdown:
            self.connect()
        self.lock.release()
        return self.session

    def connect(self):
        self.session = _connection(self.cassandra_conf, self.datacenter)

    def close_connection(self):
        self.lock.acquire()
        self.session.cluster.shutdown()
        self.session.shutdown()
        self.lock.release()
