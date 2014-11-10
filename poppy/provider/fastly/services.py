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

from poppy.common import decorators
from poppy.provider import base


class ServiceController(base.ServiceBase):
    """Fastly Service Controller Class."""

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver

    def update(self, provider_service_id, service_obj):
        return self.responder.updated(provider_service_id)

    def create(self, service_obj):

        try:
            # Create a new service
            service = self.client.create_service(self.current_customer.id,
                                                 service_obj.name)

            # Create a new version of the service.
            service_version = self.client.create_version(service.id)

            # Create the domain for this service
            for domain in service_obj.domains:
                domain = self.client.create_domain(service.id,
                                                   service_version.number,
                                                   domain.domain)

            # TODO(tonytan4ever): what if check_domains fail ?
            # For right now we fail the who create process.
            # But do we want to fail the whole service create ? probably not.
            # we need to carefully divise our try_catch here.
            domain_checks = self.client.check_domains(service.id,
                                                      service_version.number)
            links = [{"href": '.'.join([domain_check.domain.name,
                                        "global.prod.fastly.net"]),
                      "rel": 'access_url'}
                     for domain_check in domain_checks]

            for origin in service_obj.origins:
                # Create the origins for this domain
                self.client.create_backend(service.id,
                                           service_version.number,
                                           origin.origin.replace(":", "-"),
                                           origin.origin,
                                           origin.ssl,
                                           origin.port
                                           )

            # TODO(tonytan4ever): To incorporate caching, restriction change
            # once standarnd/limitation on these service details have been
            # figured out

            # activate latest version of this fastly service
            service_versions = self.client.list_versions(service.id)
            latest_version_number = max([version.number
                                         for version in service_versions])
            self.client.activate_version(service.id, latest_version_number)

            return self.responder.created(service.id, links)

        except fastly.FastlyError:
            return self.responder.failed("failed to create service")
        except Exception:
            return self.responder.failed("failed to create service")

    def delete(self, provider_service_id):
        try:
            # Delete the service
            fastly_service = self.client.get_service_details(
                provider_service_id
            )
            # deactivate the service first
            self.client.deactivate_version(
                provider_service_id,
                fastly_service.active_version['number']
            )
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

    def purge(self, service_id, purge_urls=None):
        try:
            # Get the service
            if purge_urls is None:
                self.client.purge_service(service_id)
                return self.responder.purged(service_id, purge_urls=purge_urls)
            else:
                service_domains = self.client.list_domains(service_id)
                domain_names = [service_domain.name for service_domain
                                in service_domains]
                for purge_url in purge_urls:
                    for domain_name in domain_names:
                        self.client.purge_url(domain_name, purge_url)
                return self.responder.purged(service_id, purge_urls=purge_urls)
        except fastly.FastlyError:
            return self.responder.failed("failed to PURGE service")

    @decorators.lazy_property(write=False)
    def current_customer(self):
        return self.client.get_current_customer()
