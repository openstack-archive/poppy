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
from poppy.model import service
from poppy.storage import base


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.created_service_ids = []
        self.created_service_names = []

    @property
    def session(self):
        return self._driver.database

    def list(self, project_id, marker=None, limit=None):
        provider_details_list = {
            'MaxCDN': json.dumps(
                {'id': 11942,
                 'access_urls': [{'operator_url': 'mypullzone.netdata.com'}]}),
            'Mock': json.dumps(
                {'id': 73242,
                 'access_urls': [{'operator_url': 'mycdn.mock.com'}]}),
            'CloudFront': json.dumps(
                {'id': '5ABC892',
                 'access_urls': [{'operator_url': 'cf123.cloudcf.com'}]}),
            'Fastly': json.dumps(
                {'id': 3488,
                 'access_urls':
                    [{'operator_url': 'mockcf123.fastly.prod.com'}]})}

        services = []
        for i in self.created_service_ids:
            services = [{'service_id': i,
                         'name': i,
                         'domains': [json.dumps(
                             {'domain': 'www.mywebsite.com'})
                         ],
                         'origins': [json.dumps({'origin': 'mywebsite.com',
                                                 'port': 80,
                                                 'ssl': False})],
                         'flavor_id': 'standard',
                         'caching': [{'name': 'default',
                                      'ttl': 3600},
                                     {'name': 'home',
                                      'ttl': 17200,
                                      'rules': [
                                          {'name': 'index',
                                           'request_url': '/index.htm'}
                                      ]},
                                     {'name': 'images',
                                      'ttl': 12800,
                                      'rules': [{'name': 'images',
                                                 'request_url': '*.png'}]}],
                         'restrictions': [{'name': 'website only',
                                           'rules': [{'name': 'mywebsite.com',
                                                      'http_host':
                                                      'www.mywebsite.com'}]}],
                         'provider_details': provider_details_list}]

        services_result = []
        for r in services:
            service_result = self.format_result(r)
            services_result.append(service_result)

        return services_result

    def get(self, project_id, service_id):
        # get the requested service from storage
        if service_id not in self.created_service_ids:
            raise ValueError("service: % does not exist")
        else:
            origin_json = json.dumps({'origin': 'mywebsite.com',
                                      'port': 80,
                                      'ssl': False})
            domain_json = json.dumps({'domain': 'www.mywebsite.com'})
            provider_details_list = {
                'MaxCDN': json.dumps(
                    {'id': 11942,
                     'access_urls': [
                         {'operator_url': 'mypullzone.netdata.com'}]}),
                'Mock': json.dumps(
                    {'id': 73242,
                     'access_urls': [
                         {'operator_url': 'mycdn.mock.com'}]}),
                'CloudFront': json.dumps(
                    {'id': '5ABC892',
                     'access_urls': [
                         {'operator_url': 'cf123.cloudcf.com'}]}),
                'Fastly': json.dumps(
                    {'id': 3488,
                     'access_urls':
                        [{'operator_url': 'mockcf123.fastly.prod.com'}]})}

            service_dict = {'service_id': service_id,
                            'name': service_id,
                            'domains': [domain_json],
                            'origins': [origin_json],
                            'flavor_id': 'standard',
                            'caching': [{'name': 'default',
                                         'ttl': 3600},
                                        {'name': 'home',
                                         'ttl': 17200,
                                         'rules': [
                                             {'name': 'index',
                                              'request_url': '/index.htm'}]},
                                        {'name': 'images',
                                         'ttl': 12800,
                                         'rules': [{'name': 'images',
                                                    'request_url': '*.png'}]}],
                            'restrictions': [{'name': 'website only',
                                              'rules': [
                                                  {'name': 'mywebsite.com',
                                                   'http_host':
                                                   'www.mywebsite.com'}]}],
                            'provider_details': provider_details_list}
            service_result = self.format_result(service_dict)
            return service_result

    def create(self, project_id, service_obj):
        if service_obj.service_id in self.created_service_ids:
            raise ValueError("Service %s already exists." %
                             service_obj.service_id)
        elif service_obj.name in self.created_service_names:
            raise ValueError("Service %s already exists." % service_obj.name)
        else:
            # TODO(amitgandhinz): append the entire service
            # instead of just the name
            self.created_service_ids.append(service_obj.service_id)
            self.created_service_names.append(service_obj.name)

    def update(self, project_id, service_id, service_json):
        # update configuration in storage
        return ''

    def delete(self, project_id, service_id):
        if (service_id in self.created_service_ids):
            self.created_service_ids.remove(service_id)

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

    def update_provider_details(self, project_id, service_name,
                                provider_details):
        pass

    @staticmethod
    def format_result(result):
        service_id = result.get('service_id')
        name = result.get('service_name')
        origins = [json.loads(o) for o in result.get('origins', [])]
        domains = [json.loads(d) for d in result.get('domains', [])]
        origins = [origin.Origin(o['origin'],
                                 o.get('port', 80),
                                 o.get('ssl', False))
                   for o in origins]
        domains = [domain.Domain(d['domain']) for d in domains]
        flavor_id = result.get('flavor_id')
        s = service.Service(service_id, name, domains, origins, flavor_id)
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
