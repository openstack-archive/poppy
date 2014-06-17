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

class ServicesController(base.ServicesBase):

    def __init__(self, *args, **kwargs):
        super(ServicesController, self).__init__(*args, **kwargs)

        self._session = self.driver.service_database


    def list(self):
        services = {
                "links": [
                    {
                      "rel": "next",
                      "href": "/v1.0/services?marker=www.myothersite.com&limit=20"
                    }
                ],
                "services" : [
                    {
                        "domains": [
                            {
                                "domain": "www.mywebsite.com"
                            }
                        ],
                        "origins": [
                            {
                                "origin": "mywebsite.com",
                                "port": 80,
                                "ssl": False
                            }
                        ],
                        "caching": [
                            {   "name" : "default", "ttl" : 3600 },
                            { 
                                "name" : "home", 
                                "ttl" : 17200, 
                                "rules" : [
                                    { "name" : "index", "request_url" : "/index.htm" }
                                ] 
                            },
                            { 
                                "name" : "images",
                                "ttl" : 12800, 
                                "rules" : [
                                    { "name" : "images", "request_url" : "*.png" }
                                ] 
                            }
                        ],
                        "restrictions" : [ 
                            { 
                                "name" : "website only", 
                                "rules" : [ { "name" : "mywebsite.com", "http_host" : "www.mywebsite.com" } ] 
                            } 
                        ],
                        "links" : [
                            {
                                "href": "/v1.0/services/mywebsite",
                                "rel" : "self"
                            }
                        ]
                    }
                ]
            }

        return services
    
    def get(self):
        # get the requested service from storage
        print "get service"

    def create(self, service_name, service_json):

        # create the service in storage
        service = service_json

        """Creates a new service"""
        args = (service_name, uuid.uuid1())
        res = self._session.execute(CQL_CREATE_SERVICE, args)

        print "stored new record in cassandra"

        
        # create at providers
        providers = super(ServicesController, self).create(service_name, service)

        return providers

    def update(self, service_name, service_json):
        # update configuration in storage

        # update at providers
        return super(ServicesController, self).update(service_name, service_json)

    def delete(self, service_name):
        # delete local configuration from storage

        # delete from providers
        return super(ServicesController, self).delete(service_name)

    
