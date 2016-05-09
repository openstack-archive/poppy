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

import mock
from oslo_config import cfg

from poppy.storage.sqlalchemy import driver
from tests.unit import base


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


class SqlalchemyStorageDriverTests(base.TestCase):

    @mock.patch.object(driver, 'SQLALCHEMY_OPTIONS', new=SQLALCHEMY_OPTIONS)
    def setUp(self):
        super(SqlalchemyStorageDriverTests, self).setUp()
        conf = cfg.ConfigOpts()
        conf.register_opts(SQLALCHEMY_OPTIONS,
                           group=driver.SQLALCHEMY_GROUP)
        self.sqlalchemy_driver = driver.SqlalchemyStorageDriver(conf)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEqual(
            self.sqlalchemy_driver.sqlalchemy_conf['sql_connection'],
            'sqlite://')
        self.assertEqual(
            self.sqlalchemy_driver.sqlalchemy_conf.max_retries,
            10)

    def test_storage_name(self):
        self.assertEqual('Sqlalchemy', self.cassandra_driver.storage_name)

    def test_is_alive_no_connection(self):
        """No connection test for checking the health of Sqlalchemy."""
        self.skipTest('Too slow, need to mock exception')

    def test_is_alive_with_exception(self):
        """Broken connection test for checking the health of Sqlalchemy."""
        self.skipTest('Too slow, need to mock exception')

    def test_is_alive(self):
        """Happy path test for checking the health of Sqlalchemy."""
        self.skipTest('Too slow, need to mock exception')
