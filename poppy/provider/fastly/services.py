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

from poppy.provider import base


class ServiceController(base.ServiceBase):

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.current_customer = self.client.get_current_customer()

    def update(self, provider_service_id, service_json):
        return self.responder.updated(provider_service_id)

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

            # TODO(tonytan4ever): what if check_domains fail ?
            # For right now we fail the who create process.
            # But do we want to fail the whole service create ? probably not.
            # we need to carefully divise our try_catch here.
            links = [{"href": '.'.join([domain_dict['name'], suffix]),
                      "rel": 'access_url'}
                     for domain_dict, suffix, enabled in
                     self.client.check_domains(service.id,
                                               service_version.number)
                     if enabled]

            for origin in service_json["origins"]:
                # Create the origins for this domain
                self.client.create_backend(service.id,
                                           service_version.number,
                                           origin["origin"],
                                           origin["origin"],
                                           origin["ssl"],
                                           origin["port"]
                                           )
            return self.responder.created(service.id, links)

        except fastly.FastlyError:
            return self.responder.failed("failed to create service")
        except Exception:
            return self.responder.failed("failed to create service")

    def delete(self, provider_service_id):
        try:
            # Delete the service
            self.client.delete_service(provider_service_id)

            return self.responder.deleted(provider_service_id)
        except Exception:
            return self.responder.failed("failed to delete service")

    def get(self, service_name):
        try:
            # Get the service
            service = self.client.get_service_by_name(service_name)
            service_version = self.client.list_versions(service.id)

            # TODO(malini): Use the active version, instead of the first
            # available. This will need to wait until the create service is
            # implemented completely.
            version = service_version[0]['number']

            # Get the Domain List
            domains = self.client.list_domains(service.id, version)
            domain_list = [domain['name'] for domain in domains]

            # Get the Cache List
            cache_setting_list = self.client.list_cache_settings(
                service.id, version)

            cache_list = [{'name': item['name'], 'ttl': int(item['ttl']),
                           'rules': item['cache_condition']}
                          for item in cache_setting_list]

            # Get the Origin List
            backends = self.client.list_backends(service.id, version)
            origin = backends[0]['address']
            port = backends[0]['port']
            ssl = backends[0]['use_ssl']

            origin_list = [{'origin': origin, 'port': port, 'ssl': ssl}]

            return self.responder.get(domain_list, origin_list, cache_list)

        except fastly.FastlyError:
            return self.responder.failed("failed to GET service")
        except Exception:
            return self.responder.failed("failed to GET service")
