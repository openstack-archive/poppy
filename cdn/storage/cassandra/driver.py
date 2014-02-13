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

from cassandra.cluster import Cluster

from cdn.common import decorators
from cdn.openstack.common import log as logging
from cdn import storage
from cdn.storage.cassandra import controllers

from oslo.config import cfg

LOG = logging.getLogger(__name__)

CASSANDRA_OPTIONS = [
    cfg.StrOpt('database', default='cdn', help='Database name'),
    cfg.StrOpt('cluster', help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='cdn',
               help='Keyspace for all queries made in session'),
]

CASSANDRA_GROUP = 'drivers:storage:cassandra'


def _connection(conf):
    cluster = Cluster(conf.cluster)
    session = cluster.connect(conf.keyspace)

    return session


class StorageDriver(storage.StorageDriverBase):

    def __init__(self, conf):
        super(StorageDriver, self).__init__(conf)

        self.conf.register_opts(CASSANDRA_OPTIONS,
                                group=CASSANDRA_GROUP)
        self.cassandra_conf = self.conf[CASSANDRA_GROUP]

    def is_alive(self):
        return True

    @decorators.lazy_property(write=False)
    def host_controller(self):
        return controllers.HostController()
