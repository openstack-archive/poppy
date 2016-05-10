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

    def _create_new_service_version(self, service, service_obj):
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
        # we need to carefully devise our try_catch here.
        domain_checks = self.client.check_domains(service.id,
                                                  service_version.number)
        links = [{"href": '.'.join([domain_check.domain.name,
                                    "global.prod.fastly.net"]),
                  "rel": 'access_url',
                  "domain": domain_check.domain.name}
                 for domain_check in domain_checks]

        for origin in service_obj.origins:
            # Create the origins for this domain
            self.client.create_backend(service.id,
                                       service_version.number,
                                       origin.origin.replace(":", "-"),
                                       origin.origin,
                                       origin.ssl,
                                       origin.port)

        # Fastly referrer restriction implementation
        # get a list of referrer restriction domains/hosts
        referrer_restriction_list = [rule.referrer
                                     for restriction in
                                     service_obj.restrictions
                                     for rule in restriction.rules
                                     if hasattr(rule, 'referrer')]

        # if there is a referrer_restricted host/domains at all in
        # this list. It is equivalent of 'if the list is not empty' and
        # if any item is not None
        if any(referrer_restriction_list):
            host_pattern_statement = ' || '.join(
                ['req.http.referer' ' !~ "%s"' % referrer
                 for referrer in referrer_restriction_list
                 if referrer is not None])
            condition_stmt = ('req.http.referer && (%s)'
                              % host_pattern_statement)
            # create a fastly condition for referer restriction
            request_condition = self.client.create_condition(
                service.id,
                service_version.number,
                'Referrer Restriction Matching Rules',
                fastly.FastlyConditionType.REQUEST,
                condition_stmt,
                priority=10
            )
            # apply this condition with a 403 response so
            # any request that does not from a list of permitted
            # domains will be locked (getting a 403)
            self.client.create_response_object(
                service.id,
                service_version.number,
                'Referrer Restriction response rule(s)',
                status='403',
                content='Referring from a non-permitted domain',
                request_condition=request_condition.name
            )

        # Fastly caching rule implementation
        for caching_rule in service_obj.caching:
            if caching_rule.name.lower() == 'default':
                self.client.update_settings(service.id,
                                            service_version.number,
                                            {'general.default_ttl':
                                             caching_rule.ttl
                                             }
                                            )
            else:
                # create condition first
                url_matching_stament = ' || '.join(
                    ['req.url' ' ~ "^%s"' % rule.request_url
                     for rule in caching_rule.rules])
                # create a fastly condition for referer restriction
                cachingrule_request_condition = self.client.create_condition(
                    service.id,
                    service_version.number,
                    'CachingRules condition for %s' % caching_rule.name,
                    fastly.FastlyConditionType.CACHE,
                    url_matching_stament,
                    priority=10
                )
                # create caching settings
                self.client.create_cache_settings(
                    service.id,
                    service_version.number,
                    caching_rule.name,
                    None,  # action field
                    ttl=caching_rule.ttl,
                    stale_ttl=0,
                    cache_condition=cachingrule_request_condition.name
                )

        # activate latest version of this fastly service
        service_versions = self.client.list_versions(service.id)
        latest_version_number = max([version.number
                                     for version in service_versions])
        self.client.activate_version(service.id, latest_version_number)

        return links

    def create(self, service_obj):
        try:
            # Create a new service
            service = self.client.create_service(self.current_customer.id,
                                                 service_obj.name)
            links = self._create_new_service_version(service, service_obj)
            return self.responder.created(service.id, links)
        except fastly.FastlyError as e:
            return self.responder.failed(str(e))
        except Exception as e:
            return self.responder.failed(str(e))

    def update(self,
               provider_service_id,
               service_obj):
        try:
            service = self.client.get_service_details(provider_service_id)
            links = self._create_new_service_version(service, service_obj)
            return self.responder.updated(service.id, links)
        except fastly.FastlyError as e:
            return self.responder.failed(str(e))
        except Exception as e:
            return self.responder.failed(str(e))

    def delete(self, project_id, provider_service_id):
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
        except Exception as e:
            return self.responder.failed(str(e))

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

        except fastly.FastlyError as e:
            return self.responder.failed(str(e))
        except Exception as e:
            return self.responder.failed(str(e))

    def purge(self, service_id, hard=True, purge_url='/*'):
        try:
            # Get the service
            if purge_url == '/*':
                self.client.purge_service(service_id)
                return self.responder.purged(service_id, purge_url=purge_url)
            else:
                service = self.client.get_service_details(service_id)
                version = service.active_version['number']
                service_domains = self.client.list_domains(service_id, version)
                domain_names = [service_domain.name for service_domain
                                in service_domains]
                for domain_name in domain_names:
                    self.client.purge_url(domain_name, purge_url)

                return self.responder.purged(service_id, purge_url=purge_url)
        except fastly.FastlyError as e:
            return self.responder.failed(str(e))

    @decorators.lazy_property(write=False)
    def current_customer(self):
        return self.client.get_current_customer()

    def get_provider_service_id(self, service_obj):
        return service_obj.service_id

    def get_metrics_by_domain(self, project_id, domain_name, regions,
                              **extras):
        '''Use Fastly's API to get the metrics by domain.'''
        return []
