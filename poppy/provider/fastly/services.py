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

import json

import fastly

from poppy.provider import base


class ServiceController(base.ServiceBase):

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.current_customer = self.client.get_current_customer()

    def update(self, provider_detail, service_json):
        provider_details_dict = json.loads(provider_detail)
        service_id = provider_details_dict['id']
        return self.responder.updated(service_id)

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
                self.client.create_backend(service.id,
                                           service_version.number,
                                           origin["origin"],
                                           origin["origin"],
                                           origin["ssl"],
                                           origin["port"]
                                           )

            return self.responder.created(service.name)

        except fastly.FastlyError:
            return self.responder.failed("failed to create service")
        except Exception:
            return self.responder.failed("failed to create service")

    def delete(self, provider_details):
        try:
            provider_details_dict = json.loads(provider_details)
            service_id = provider_details_dict['id']

            # Delete the service
            self.client.delete_service(service_id)

            return self.responder.deleted(service_id)
        except Exception:
            return self.responder.failed("failed to delete service")
