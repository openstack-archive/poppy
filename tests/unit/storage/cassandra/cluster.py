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


from tests.unit.storage.cassandra import mockcassandra
from tests.unit.storage.cassandra import session

class Cluster(object):

    def __init__(self, hosts = None):
        self.cassandra = mockcassandra.Cassandra()

    def connect(self, keyspace=None):
        connection = session.Session(self.cassandra)
        if keyspace:
            connection.set_keyspace(keyspace)
        return connection

    def shutdown(self):
        pass
