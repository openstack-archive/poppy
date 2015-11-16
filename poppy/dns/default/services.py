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
import random

from poppy.dns import base


class ServicesController(base.ServicesBase):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.driver = driver
        self.shared_ssl_shards = 5

    def update(self, service_old, service_updates, responders):
        """Default DNS update.

        :param service_old: previous service state
        :param service_updates: updates to service state
        :param responders: responders from providers
        """

        dns_details = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                access_urls = []
                for link in responder[provider_name]['links']:
                    access_url = {
                        'domain': link['domain'],
                        'provider_url': link['href'],
                        'operator_url': link['href']}
                    access_urls.append(access_url)
                dns_details[provider_name] = {'access_urls': access_urls}
        return self.responder.created(dns_details)

    def delete(self, provider_details):
        """Default DNS delete.

        :param provider_details
        """

        dns_details = {}
        for provider_name in provider_details:
            dns_details[provider_name] = self.responder.deleted({})
        return dns_details

    def create(self, responders):
        """Default DNS create.

        :param responders: responders from providers
        """

        dns_details = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                access_urls = []
                for link in responder[provider_name]['links']:
                    access_url = {
                        'domain': link['domain'],
                        'provider_url': link['href'],
                        'operator_url': link['href']}
                    access_urls.append(access_url)
                dns_details[provider_name] = {'access_urls': access_urls}
        return self.responder.created(dns_details)

    def generate_shared_ssl_domain_suffix(self):
        """Default DNS Generate a shared ssl domain suffix,

        to be used with manager for shared ssl feature

        """
        shard_ids = [i for i in range(1, self.shared_ssl_shards + 1)]
        random.shuffle(shard_ids)
        for shard in shard_ids:
            yield 'scdn{0}.secure.defaultcdn.com'.format(shard)
