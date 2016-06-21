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

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model.helpers import restriction
from poppy.model.helpers import rule
from poppy.model import service
from poppy.storage import base

created_services = {}
created_service_ids = []
claimed_domains = []
project_id_service_limit = {}
service_count_per_project_id = {}


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.created_service_ids = created_service_ids
        self.created_services = created_services
        self.claimed_domains = claimed_domains
        self.project_id_service_limit = project_id_service_limit
        self.default_max_service_limit = 20
        self.service_count_per_project_id = service_count_per_project_id

    @property
    def session(self):
        return self._driver.database

    def get_services(self, project_id, marker=None, limit=None):
        services = []
        for service_id in self.created_services:
            services.append(self.created_services[service_id])

        services_result = []
        for r in services:
            service_result = self.format_result(r)
            services_result.append(service_result)

        return services_result

    def get_service(self, project_id, service_id):
        # get the requested service from storage
        if service_id not in self.created_service_ids:
            raise ValueError("service {0} does not exist".format(service_id))
        else:
            service_dict_in_cache = self.created_services[service_id]
            service_result = self.format_result(service_dict_in_cache)
            service_result._status = 'deployed'
            return service_result

    def create_service(self, project_id, service_obj):
        if service_obj.service_id in self.created_service_ids:
            raise ValueError("Service %s already exists." %
                             service_obj.service_id)

        self.created_service_ids.append(service_obj.service_id)
        self.created_services[service_obj.service_id] = service_obj.to_dict()
        for domain_obj in service_obj.domains:
            self.claimed_domains.append(domain_obj.domain)
        try:
            self.service_count_per_project_id[project_id] += 1
        except KeyError:
            self.service_count_per_project_id[project_id] = 1

    def set_service_limit(self, project_id, project_limit):
        self.project_id_service_limit[project_id] = project_limit

    def get_service_limit(self, project_id):
        try:
            return self.project_id_service_limit[project_id]
        except KeyError:
            return self.default_max_service_limit

    def get_service_count(self, project_id):
        try:
            return self.service_count_per_project_id[project_id]
        except KeyError:
            return 0

    def get_services_by_status(self, status):

        complete_results = []
        for created_service in self.created_services:
            service_obj = self.format_result(
                self.created_services[created_service]
            )
            if service_obj._status == status:
                complete_results.append(created_service.service_id)

        return complete_results

    def update_service(self, project_id, service_id, service_json):
        # update configuration in storage
        if service_json.service_id in self.created_service_ids \
                and service_json.service_id == service_id:
            if not any([domain_obj for domain_obj in service_json.domains
                        if self.domain_exists_elsewhere(domain_obj,
                                                        service_id)]):
                self.created_services[service_id] = service_json.to_dict()
                for domain_obj in service_json.domains:
                    if domain_obj not in self.claimed_domains:
                        self.claimed_domains.append(domain_obj.domain)
            else:
                raise ValueError("Domain has already been taken")

    def update_state(self, project_id, service_id, state):
        """update_state

        Update service state

        :param project_id
        :param service_id
        :param state

        :returns service_obj
        """

        service_obj = self.get_service(project_id, service_id)
        service_obj.operator_status = state
        self.update_service(project_id, service_id, service_obj)

        return self.get_service(project_id, service_id)

    def delete_service(self, project_id, service_id):
        if service_id in self.created_service_ids:
            self.created_service_ids.remove(service_id)
        try:
            self.service_count_per_project_id[project_id] -= 1
        except KeyError:
            self.service_count_per_project_id[project_id] = 0

    def get_provider_details(self, project_id, service_id):
        if service_id not in self.created_service_ids:
            raise ValueError("service: % does not exist")
        else:
            return {
                'MaxCDN': provider_details.ProviderDetail(
                    provider_service_id=11942,
                    name='my_service_name',
                    access_urls=['my_service_name'
                                 '.mycompanyalias.netdna-cdn.com']),
                'Fastly': provider_details.ProviderDetail(
                    provider_service_id=3488,
                    name="my_service_name",
                    access_urls=['my_service_name'
                                 '.global.prod.fastly.net']),
                'CloudFront': provider_details.ProviderDetail(
                    provider_service_id=5892,
                    access_urls=['my_service_name'
                                 '.gibberish.amzcf.com']),
                'Mock': provider_details.ProviderDetail(
                    provider_service_id="73242",
                    access_urls=['my_service_name.mock.com'])}

    def set_service_provider_details(self, project_id, service_id, status):
        pass

    def update_provider_details(self, project_id, service_name,
                                new_provider_details):
        pass

    def domain_exists_elsewhere(self, domain_name, service_id):
        return domain_name in self.claimed_domains

    def get_service_details_by_domain_name(self, domain_name,
                                           project_id=None):
        for service_id in self.created_services:
            service_dict_in_cache = self.created_services[service_id]
            if domain_name in [d['domain']
                               for d in service_dict_in_cache['domains']]:
                service_result = self.format_result(service_dict_in_cache)
                service_result._status = 'deployed'
                return service_result

    @staticmethod
    def format_result(result):
        service_id = result.get('service_id')
        name = str(result.get('service_name'))
        origins = [o for o in result.get('origins', [])]
        domains = [d for d in result.get('domains', [])]
        origins = [origin.Origin(o['origin'],
                                 hostheadertype='domain',
                                 hostheadervalue='blog.mywebsite.com',
                                 port=o.get('port', 80),
                                 ssl=o.get('ssl', False))
                   for o in origins]
        domains = [domain.Domain(d['domain'], d['protocol'], d['certificate'])
                   for d in domains]
        restrictions = [restriction.Restriction(
            r.get('name'),
            r.get('access', 'whitelist'),
            [rule.Rule(r_rule.get('name'),
                       referrer=r_rule.get('referrer'),
                       client_ip=r_rule.get('client_ip'),
                       geography=r_rule.get('geography'),
                       request_url=r_rule.get('request_url', "/*") or "/*")
             for r_rule in r['rules']])
            for r in result.get('restrictions', [])]

        flavor_id = result.get('flavor_id')
        s = service.Service(service_id, name, domains, origins, flavor_id,
                            restrictions=restrictions)
        provider_detail_results = result.get('provider_details') or {}
        provider_details_dict = {}
        for provider_name in provider_detail_results:
            provider_detail_dict = json.loads(
                provider_detail_results[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            provider_details_dict[provider_name] = provider_detail_obj
        s.provider_details = provider_details_dict
        return s
