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

from poppy.storage import base


class ServicesController(base.ServicesController):

    @property
    def session(self):
        return self._driver.service_database

    def list(self, project_id, marker=None, limit=None):
        services = [
            {
                "name": "mockdb1_service_name",
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
                    {"name": "default", "ttl": 3600},
                    {
                        "name": "home",
                        "ttl": 17200,
                        "rules": [
                                {"name": "index",
                                 "request_url": "/index.htm"}
                        ]
                    },
                    {
                        "name": "images",
                        "ttl": 12800,
                        "rules": [
                                {"name": "images", "request_url": "*.png"}
                        ]
                    }
                ],
                "restrictions": [
                    {
                        "name": "website only",
                        "rules": [
                                {
                                    "name": "mywebsite.com",
                                    "http_host": "www.mywebsite.com"
                                }
                        ]
                    }
                ],
            }
        ]

        return services

    def get(self, project_id, service_name):
        # get the requested service from storage
        service = {
            "name": service_name,
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
                {"name": "default", "ttl": 3600},
                {
                    "name": "home",
                            "ttl": 17200,
                            "rules": [
                                {"name": "index",
                                 "request_url": "/index.htm"}
                            ]
                },
                {
                    "name": "images",
                            "ttl": 12800,
                            "rules": [
                                {"name": "images", "request_url": "*.png"}
                            ]
                }
            ],
            "restrictions": [
                {
                    "name": "website only",
                            "rules": [
                                {
                                    "name": "mywebsite.com",
                                    "http_host": "www.mywebsite.com"
                                }
                            ]
                }
            ],
        }
        return service

    def create(self, project_id, service_name, service_json):

        return ""

    def update(self, project_id, service_name, service_json):
        # update configuration in storage
        return ""

    def delete(self, project_id, service_name):

        # delete from providers
        return ""
