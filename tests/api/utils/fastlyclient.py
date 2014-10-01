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

from cafe.engine.http import client
import fastly


class FastlyClient(client.AutoMarshallingHTTPClient):

    """Client objects for Fastly api calls."""

    def __init__(self, api_key, email, password, serialize_format="json",
                 deserialize_format="json"):
        super(FastlyClient, self).__init__(serialize_format,
                                           deserialize_format)
        self.client = fastly.connect(api_key)
        self.client.login(email, password)

        self.serialize = serialize_format
        self.deserialize_format = deserialize_format

    def get_service(self, service_name):
        # Get the service
        try:
            service = self.client.get_service_by_name(service_name)
        except fastly.FastlyError as e:
            assert False, e

        service_version = self.client.list_versions(service.id)

        # The create service api_call updates the domain, origin & cache
        # settings in second version of the service. The version # will be the
        # value of 'number' in the second element of the list returned by
        # self.client.list_versions(service.id) call above
        version = service_version[1].number

        # Get the Domain List
        domains = self.client.list_domains(service.id, version)
        domain_list = [{'domain': domain.name} for domain in domains]

        # Get the Cache List
        cache_setting_list = self.client.list_cache_settings(
            service.id, version)

        cache_list = [{'name': item['name'], 'ttl': int(item['ttl']),
                       'rules': item['cache_condition']}
                      for item in cache_setting_list]

        # Get the Origin List
        try:
            backends = self.client.list_backends(service.id, version)
            origin = backends[0].address
            port = backends[0].port
            ssl = backends[0].use_ssl
            origin_list = [{'origin': origin, 'port': port, 'ssl': ssl}]
        except IndexError:
            assert False, 'Empty Backend in Fastly'
        except fastly.FastlyError as e:
            assert False, e

        return {'domain_list': domain_list,
                'origin_list': origin_list,
                'caching_list': cache_list}
