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

import fastly
import json

from cdn.provider import base


class HostController(base.HostBase):

    def __init__(self, driver):
        super(HostController, self).__init__()

        self.client = driver.client
        self.current_customer = self.client.get_current_customer()

        self.provider_resp = base.ProviderResponse("fastly")

    def update(self):
        print "update services"

    def create(self, service_name, service_json):

        try:
            # Create a new service
            service = self.client.create_service(self.current_customer.id,
                service_name)

            # Create a new version of the service.
            service_version = self.client.create_version(service.id)

            # Create the domain for this service
            for domain in service_json["domains"]:
                domain = self.client.create_domain(service.id, 
                    service_version.number,
                    domain["domain"])

            for origin in service_json["origins"]:
                # Create the origins for this domain
                backend = self.client.create_backend(service.id,
                    service_version.number,
                    origin["origin"],
                    origin["origin"],
                    origin["ssl"],
                    origin["port"]
                    )

            return self.provider_resp.created(service.name)

        except fastly.FastlyError:
            return self.provider_resp.failed("failed to create service")
        except:
            return self.provider_resp.failed("failed to create service")

    def delete(self, service_name):
        try:
            # Get the service
            service = self.client.get_service_by_name(service_name)
            # Delete the service
            deleted = self.client.delete_service(service.id)

            return self.provider_resp.deleted(service_name)
        except:
            return self.provider_resp.failed("failed to delete service")


   