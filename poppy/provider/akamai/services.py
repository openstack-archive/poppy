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

from poppy.common import decorators
from poppy.openstack.common import log
from poppy.provider import base

LOG = log.getLogger(__name__)


class ServiceController(base.ServiceBase):

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.base_url = self.driver.akamai_base_url
        self.base_ccu_url = self.driver.akamai_base_ccu_url
        self.reuest_header = {'Content-type': 'application/json',
                              'Accept': 'text/plain'}

    def create(self, service_obj):
        post_data = {
            'rules': []
        }

        # for now global level akamai only supports 1 origin match global
        # * url. At this point we are guaranteed there is at least 1 origin
        # in incoming service_obj
        # form all origin rules for this service
        for origin in service_obj.origins:
            rule_dict_template = {
                'matches': [],
                'behaviors': []
            }

            origin_behavior_dict = {
                'name': 'origin',
                'value': '-',
                'params': {
                    # missing digitalProperty(domain) for now
                    'originDomain': '',
                    'hostHeaderType': 'digital_property',
                    'cacheKeyType': 'origin',
                    'hostHeaderValue': '-',
                    'cacheKeyValue': '-'
                }
            }
            # this is the global 'url-wildcard' rule
            if origin.rules == []:
                match_rule = {
                    'name': 'url-wildcard',
                    'value': '/*'
                }
                rule_dict_template['matches'].append(match_rule)
            else:
                for rule in origin.rules:
                    match_rule = {
                        'name': 'url-path',
                        'value': rule.request_url
                    }
                    rule_dict_template['matches'].append(match_rule)

            origin_behavior_dict['params']['originDomain'] = origin.origin
            rule_dict_template['behaviors'].append(origin_behavior_dict)
            # TODO(tonytan4ever): add referer restriction once
            # referrer restriction PR gets merged
            post_data['rules'].append(rule_dict_template)

        classified_domains = self._classify_domains(service_obj.domains)

        try:
            # NOTE(tonytan4ever): for akamai it might be possible to have
            # multiple policies associated with one poppy service, so we use
            # a list to represent provide_detail id
            ids = []
            links = []
            for classified_domain in classified_domains:
                # assign the content realm to be the digital property field
                # of each group
                dp = '.'.join(classified_domain[0].split('.')[-2:])

                for rule in post_data['rules']:
                    for behavior in rule['behaviors']:
                        behavior['params']['digitalProperty'] = dp

                resp = self.client.put(self.base_url.format(
                    policy_name=classified_domain[0]),
                    data=json.dumps(post_data),
                    headers=self.reuest_header)
                LOG.info('akamai response code: %s' % resp.status_code)
                LOG.info('akamai response text: %s' % resp.text)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)
                ids.append(classified_domain[0])
                # TODO(tonytan4ever): leave empty links for now
                # may need to work with dns integration
                LOG.info('Creating policy %s on domain %s complete' %
                         (classified_domain[0], dp))
            links.append({'href': self.driver.akamai_access_url_link,
                          "rel": 'access_url'
                          })
        except Exception:
            return self.responder.failed("failed to create service")
        else:
            return self.responder.created(json.dumps(ids), links)

    def _classify_domains(self, domains_list):
        # classify domains into different categories based on first two level
        # of domains, group them together
        result_dict = {}
        for domain in domains_list:
            # get the content_realm (1st and 2nd level domain of each domains)
            content_realm = '.'.join(domain.domain.split('.')[-2:])
            if content_realm not in result_dict:
                result_dict[content_realm] = [domain.domain]
            else:
                result_dict[content_realm].append(domain.domain)
        return [domain_mapping[1] for domain_mapping in result_dict.items()]

    def get(self, service_name):
        pass

    def update(self, provider_service_id, service_obj):
        pass

    def delete(self, provider_service_id):
        # delete needs to provide a list of policy id/domains
        # then delete them accordingly
        try:
            policies = json.loads(provider_service_id)
        except Exception:
            # raise a more meaningful error for debugging info
            try:
                raise RuntimeError('Mal-formed Akaimai policy ids: %s' %
                                   provider_service_id)
            except Exception:
                return self.responder.failed("failed to delete service")
        try:
            for policy in policies:
                LOG.info('Starting to delete policy %s' % policy)
                resp = self.client.delete(self.base_url.format(
                                          policy_name=policy))
                LOG.info('akamai response code: %s' % resp.status_code)
                LOG.info('akamai response text: %s' % resp.text)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)
        except Exception:
            return self.responder.failed("failed to delete service")
        else:
            return self.responder.deleted(provider_service_id)

    def purge(self, service_id, purge_urls=None):
        pass

    @decorators.lazy_property(write=False)
    def current_customer(self):
        return None
