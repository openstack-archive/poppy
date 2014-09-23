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

from cassandra import cluster
from cassandra import query

from poppy.openstack.common import log as logging
from poppy.storage import base
from poppy.storage.cassandra import controllers

from oslo.config import cfg

LOG = logging.getLogger(__name__)

CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='poppy',
               help='Keyspace for all queries made in session'),
]

CASSANDRA_GROUP = 'drivers:storage:cassandra'


def _connection(conf):
    cassandra_cluster = cluster.Cluster(conf.cluster)
    session = cassandra_cluster.connect(conf.keyspace)
    session.row_factory = query.dict_factory

    return session


class CassandraStorageDriver(base.Driver):

    def __init__(self, conf):
        super(CassandraStorageDriver, self).__init__(conf)

        self._conf.register_opts(CASSANDRA_OPTIONS,
                                 group=CASSANDRA_GROUP)
        self.cassandra_conf = self._conf[CASSANDRA_GROUP]
        self.session = None

    def is_alive(self):
        return True

    @property
    def storage_name(self):
        """For name."""
        return 'Cassandra'

    @property
    def services_controller(self):
        return controllers.ServicesController(self)

    @property
    def flavors_controller(self):
        return controllers.FlavorsController(self)

    @property
    def database(self):
        # if the session has been shutdown, reopen a session
        if self.session is None or self.session.is_shutdown:
            self.connect()
        return self.session

    def connect(self):
        self.session = _connection(self.cassandra_conf)

    def close_connection(self):
        self.session.cluster.shutdown()
        self.session.shutdown()
