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

"""Mongodb storage driver implementation."""

import pymongo
import pymongo.errors

from cdn.common import decorators
from cdn.openstack.common import log as logging
from cdn import storage
from cdn.storage.mongodb import controllers

from oslo.config import cfg

LOG = logging.getLogger(__name__)

MONGODB_OPTIONS = [
    cfg.StrOpt('uri', help='Mongodb Connection URI'),

    # Database name
    # TODO(kgriffs): Consider local sharding across DBs to mitigate
    # per-DB locking latency.
    cfg.StrOpt('database', default='cdn', help='Database name'),

    cfg.IntOpt('max_attempts', default=1000,
               help=('Maximum number of times to retry a failed operation.'
                     'Currently only used for retrying a message post.')),

    cfg.FloatOpt('max_retry_sleep', default=0.1,
                 help=('Maximum sleep interval between retries '
                       '(actual sleep time increases linearly '
                       'according to number of attempts performed).')),

    cfg.FloatOpt('max_retry_jitter', default=0.005,
                 help=('Maximum jitter interval, to be added to the '
                       'sleep interval, in order to decrease probability '
                       'that parallel requests will retry at the '
                       'same instant.')),
]

MONGODB_GROUP = 'drivers:storage:mongodb'


def _connection(conf):
    if conf.uri and 'replicaSet' in conf.uri:
        MongoClient = pymongo.MongoReplicaSetClient
    else:
        MongoClient = pymongo.MongoClient

    return MongoClient(conf.uri)


class StorageDriver(storage.StorageDriverBase):

    def __init__(self, conf):
        super(StorageDriver, self).__init__(conf)

        self.conf.register_opts(MONGODB_OPTIONS,
                                group=MONGODB_GROUP)
        self.mongodb_conf = self.conf[MONGODB_GROUP]

    def is_alive(self):
        try:
            return 'ok' in self.connection.admin.command('ping')

        except pymongo.errors.PyMongoError:
            return False

    @decorators.lazy_property(write=False)
    def host_database(self):
        """Database dedicated to the "host" collection.

        The host collection is separated out into its own database.
        """

        name = self.mongodb_conf.database + '_host'
        return self.connection[name]

    @decorators.lazy_property(write=False)
    def connection(self):
        """MongoDB client connection instance."""
        return _connection(self.mongodb_conf)

    @decorators.lazy_property(write=False)
    def host_controller(self):
        return controllers.HostController()
