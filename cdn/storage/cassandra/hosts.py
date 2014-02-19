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

# stevedore/example/simple.py
from cdn.storage import base


class HostController(base.HostBase):

    def list(self):
        hostnames = [
            {
                'hostname': 'www.mywebsite.com',
                'description': 'My Sample Website using Cassandra'
            },
            {
                'hostname': 'www.myotherwebsite.com',
                'description': 'My Other Website'
            }
        ]

        return hostnames

    def create(self, host, desc):

        # create the hostname in storage
        hostname = [
            {
                'hostname': host,
                'description': desc
            }
        ]

        super(HostController, self).create(host)

        return hostname

    def delete(self):
        print "delete"

    def get(self):
        print "get hostname"
