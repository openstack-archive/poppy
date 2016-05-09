# Copyright (c) 2016 Rackspace, Inc.
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

"""sqlalchemy storage driver implementation."""

import multiprocessing

from oslo_config import cfg
from oslo_db.sqlalchemy import session as sas
from oslo_log import log

from poppy.storage import base
from poppy.storage.sqlalchemy import controllers


LOG = log.getLogger(__name__)

SQLALCHEMY_OPTIONS = [
    cfg.StrOpt('sql_connection', default='sqlite://',
               help='Sql connection string'),
    cfg.IntOpt('connection_debug', default=0,
               help='connection debug level'),
    cfg.IntOpt('max_pool_size', default=10,
               help='max db connection pool size'),
    cfg.IntOpt('idle_timeout', default=3600,
               help='db connection idle timeout'),
    cfg.IntOpt('retry_interval', default=10,
               help='db connection retry interval'),
    cfg.IntOpt('max_retries', default=10,
               help='db connection max retries'),
    cfg.BoolOpt('thread_checkin', default=True,
                help='db thread checkin flag'),
]

SQLALCHEMY_GROUP = 'drivers:storage:sqlalchemy'


def _connection(conf, keyspace=None):
    """connection.

    :returns session
    """
    sa_endgine = sas.create_engine(
        sql_connection=conf.sql_connection,
        connection_debug=conf.connection_debug,
        max_pool_size=conf.max_pool_size,
        #mysql_sql_mode='TRADITIONAL',
        #sqlite_fk=False,
        idle_timeout=conf.idle_timeout,
        retry_interval=conf.retry_interval,
        max_retries=conf.max_retries,
        #max_overflow=mock.ANY,
        #connection_trace=mock.ANY,
        #sqlite_synchronous=mock.ANY,
        #pool_timeout=mock.ANY,
        thread_checkin=conf.thread_checkin
    )
    session = sas.get_maker(sa_endgine)()

    return session


class SqlalchemyStorageDriver(base.Driver):
    """Cassandra Storage Driver."""

    def __init__(self, conf):
        super(SqlalchemyStorageDriver, self).__init__(conf)

        self.conf = conf
        conf.register_opts(SQLALCHEMY_OPTIONS, group=SQLALCHEMY_GROUP)
        self.sqlalchemy_conf = conf[SQLALCHEMY_GROUP]
        self.lock = multiprocessing.Lock()

    def change_config_group(self, options, group):
        self.conf.register_opts(options, group=group)
        self.cassandra_conf = self.conf[group]

    def is_alive(self):
        """Health check for SQL Database."""
        #TODO(tonytan4ever): Add healthy check for database
        return True

    @property
    def storage_name(self):
        """storage name.

        :returns 'Sqlalchemy'
        """
        return 'Sqlalchemy'

    @property
    def connection(self):
        """Sqlalchemy connection instance."""
        return _connection(self.cassandra_conf, self.datacenter)

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
            self.session.close()
            self.session = None
        finally:
            if lock_success:
                self.lock.release()
