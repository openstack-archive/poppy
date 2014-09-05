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

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model import service
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

        services_result = []
        for r in services:
            name = r.get("name", "unnamed")
            origins = r.get("origins", [])
            domains = r.get("domains", [])
            origins = [origin.Origin(d) for d in origins]
            domains = [domain.Domain(d) for d in domains]
            services_result.append(service.Service(name, domains, origins))

        return services_result

    def get(self, project_id, service_name):
        # get the requested service from storage
        service_dict = {
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

        name = service_dict.get("name", "unnamed")
        origins = service_dict.get("origins", [])
        domains = service_dict.get("domains", [])
        origins = [origin.Origin(d) for d in origins]
        domains = [domain.Domain(d) for d in domains]
        services_result = service.Service(name, domains, origins)
        return services_result

    def create(self, project_id, service_name, service_json):

        return ""

    def update(self, project_id, service_name, service_json):
        # update configuration in storage
        return ""

    def delete(self, project_id, service_name):

        # delete from providers
        return ""

    def get_provider_details(self, project_id, service_name):
        return {
            "MaxCDN": provider_details.ProviderDetail(
                provider_service_id=11942,
                name='my_service_name',
                access_urls=['my_service_name'
                             '.mycompanyalias.netdna-cdn.com']),
            "Fastly": provider_details.ProviderDetail(
                provider_service_id=3488,
                name="my_service_name",
                access_urls=['my_service_name'
                             '.global.prod.fastly.net']),
            "CloudFront": provider_details.ProviderDetail(
                provider_service_id=5892,
                access_urls=['my_service_name'
                             '.gibberish.amzcf.com']),
            "Mock": provider_details.ProviderDetail(
                provider_service_id="73242",
                access_urls=['my_service_name.mock.com'])}

    def update_provider_details(self, project_id, service_name,
                                provider_details):
        pass
