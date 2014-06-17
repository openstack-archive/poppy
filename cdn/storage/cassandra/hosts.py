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

import uuid

from cdn.storage import base

CQL_CREATE_SERVICE = '''
    INSERT INTO services (servicename, serviceid)
    VALUES (%s, %s)
'''

class HostController(base.HostBase):

    def __init__(self, *args, **kwargs):
        super(HostController, self).__init__(*args, **kwargs)

        self._session = self.driver.host_database


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
    
    def get(self):
        # get the requested hostname from storage
        print "get hostname"

    def create(self, service_name, service_json):

        # create the hostname in storage
        service = service_json

        """Creates a new service"""
        args = (service_name, uuid.uuid1())
        res = self._session.execute(CQL_CREATE_SERVICE, args)

        print "stored new record in cassandra"

        
        # create at providers
        providers = super(HostController, self).create(service_name, service)

        return providers

    def update(self, service_name, service_json):
        # update configuration in storage

        # update at providers
        return super(HostController, self).update(service_name, service_json)

    def delete(self, service_name):
        # delete local configuration from storage

        # delete from providers
        return super(HostController, self).delete(service_name)

    
