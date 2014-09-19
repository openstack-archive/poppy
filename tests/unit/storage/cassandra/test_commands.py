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
from oslo.config import cfg

from poppy.storage.cassandra import driver
from poppy.storage.cassandra import flavors
from poppy.storage.cassandra import services
from tests.unit import base
from tests.unit.storage.cassandra import cluster
from tests.unit.storage.cassandra import mockcassandra


CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='mock_poppy',
               help='Keyspace for all queries made in session'),
]


class CassandraQueriesTests(base.TestCase):

    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        super(CassandraQueriesTests, self).setUp()

        conf = cfg.ConfigOpts()
        self.mock_cluster = cluster.Cluster()
        self.session = self.mock_cluster.connect()

    def test_create_keyspace(self):
        self.session.execute('CREATE KEYSPACE poppy')

    def test_use_keyspace(self):
        self.session.execute('USE poppy')

    def test_create_table(self):
        pass

    def test_insert(self):
        pass

    def test_select(self):
        pass

    def test_delete(self):
        pass
