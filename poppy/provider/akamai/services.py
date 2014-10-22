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
    def policy_api_client(self):
        return self.driver.policy_api_client

    @property
    def ccu_api_client(self):
        return self.driver.ccu_api_client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.policy_api_base_url = self.driver.akamai_policy_api_base_url
        self.ccu_api_base_url = self.driver.akamai_ccu_api_base_url
        self.request_header = {'Content-type': 'application/json',
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
            self._process_new_origin(origin, post_data['rules'])

        # referrer restriction implementaiton for akamai
        # get a list of referrer restriction domains/hosts
        referrer_restriction_list = [rule.referrer
                                     for restriction in
                                     service_obj.restrictions
                                     for rule in restriction.rules]

        if any(referrer_restriction_list):
            referrer_blacklist_value = ''.join(['*%s*' % referrer
                                               for referrer
                                               in referrer_restriction_list
                                               if referrer is not None])
            for rule in post_data['rules']:
                self._process_referrer_restriction(referrer_blacklist_value,
                                                   rule)

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
                dp = self._process_new_domain(classified_domain,
                                              post_data['rules'])
                resp = self.policy_api_client.put(
                    self.policy_api_base_url.format(
                        policy_name=dp),
                    data=json.dumps(post_data),
                    headers=self.request_header)
                LOG.info('akamai response code: %s' % resp.status_code)
                LOG.info('akamai response text: %s' % resp.text)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)

                ids.append(dp)
                # TODO(tonytan4ever): leave empty links for now
                # may need to work with dns integration
                LOG.info('Creating policy %s on domain %s complete' %
                         (dp, ','.join(classified_domain)))
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

    def _process_new_origin(self, origin, rules_list):
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
                rule_dict_template['matches'].append(
                    match_rule)

        origin_behavior_dict['params']['originDomain'] = (
            origin.origin
        )
        rule_dict_template['behaviors'].append(
            origin_behavior_dict
        )
        # Append the new generated rules
        rules_list.append(rule_dict_template)

    def _process_new_domain(self, domain, rules_list):
        dp = '.'.join(domain[0].split('.')[-2:])

        for rule in rules_list:
            for behavior in rule['behaviors']:
                if 'params' in behavior:
                    behavior['params']['digitalProperty'] = dp
        return dp

    def _process_referrer_restriction(self, referrer_blacklist_value, rule):
        rule['behaviors'].append({
            'name': 'referer-blacklist',
            'value': referrer_blacklist_value
        })

    def get(self, service_name):
        pass

    def update(self, provider_service_id,
               service_old,
               service_updates,
               service_obj):
        # depending on domains field presented or not, do PUT/POST
        # and depending on origins field presented or not, set behavior on
        # the data or not
        try:
            # get a list of policies
            policies = json.loads(provider_service_id)
        except Exception:
            # raise a more meaningful error for debugging info
            try:
                raise RuntimeError('Mal-formed Akaimai policy ids: %s' %
                                   provider_service_id)
            except Exception:
                return self.responder.failed("failed to update service")

        ids = []
        links = []
        if len(service_obj.domains) > 0:
            # in this case we need to copy
            # and tweak the content of one old policy
            # and creates new policy for the new domains,
            # old policies ought to be deleted.
            try:
                resp = self.policy_api_client.get(
                    self.policy_api_base_url.format(
                        policy_name=policies[0]),
                    headers=self.request_header)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)
            except Exception:
                return self.responder.failed("failed to update service")
            else:
                policy_content = json.loads(resp.text)
            # Update origin if necessary
            if len(service_obj.origins) > 0:
                policy_content['rules'] = []
                for origin in service_obj.origins:
                    self._process_new_origin(origin, policy_content['rules'])

            # referrer restriction implementaiton for akamai
            # get a list of referrer restriction domains/hosts
            referrer_restriction_list = [rule.referrer
                                         for restriction in
                                         service_obj.restrictions
                                         for rule in restriction.rules]

            if any(referrer_restriction_list):
                referrer_blacklist_value = ''.join(['*%s*' % referrer
                                                   for referrer
                                                   in referrer_restriction_list
                                                   if referrer is not None])
                for rule in policy_content['rules']:
                    self._process_referrer_restriction(
                        referrer_blacklist_value, rule)

            # Update domain if necessary ( by adjust digital property)
            classified_domains = self._classify_domains(service_obj.domains)

            try:
                for classified_domain in classified_domains:
                    # assign the content realm to be the digital property field
                    # of each group
                    dp = self._process_new_domain(classified_domain,
                                                  policy_content['rules'])

                    if dp in policies:
                        # in this case we should update existing policy
                        # instead of create a new policy
                        LOG.info('Start to update policy %s' % dp)
                        resp = self.policy_api_client.put(
                            self.policy_api_base_url.format(
                                policy_name=dp),
                            data=json.dumps(policy_content),
                            headers=self.request_header)
                        policies.remove(dp)
                    else:
                        LOG.info('Start to create new policy %s' % dp)
                        resp = self.policy_api_client.put(
                            self.policy_api_base_url.format(
                                policy_name=dp),
                            data=json.dumps(policy_content),
                            headers=self.request_header)
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                    ids.append(classified_domain[0])
                    # TODO(tonytan4ever): leave empty links for now
                    # may need to work with dns integration
                    LOG.info('Creating/Updateing policy %s on domain %s '
                             'complete' % (dp, ','.join(classified_domain)))
                links.append({'href': self.driver.akamai_access_url_link,
                              'rel': 'access_url'
                              })
            except Exception:
                return self.responder.failed("failed to update service")

            try:
                for policy in policies:
                    LOG.info('Starting to delete old policy %s' % policy)
                    resp = self.policy_api_client.delete(
                        self.policy_api_base_url.format(
                            policy_name=policy))
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                    LOG.info('Delete old policy %s complete' % policy)
            except Exception:
                return self.responder.failed("failed to update service")

        else:
            # in this case we only need to adjust the existing policies
            for policy in policies:
                try:
                    resp = self.policy_api_client.get(
                        self.policy_api_base_url.format(policy_name=policy),
                        headers=self.request_header)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                except Exception:
                    return self.responder.failed("failed to update service")
                else:
                    policy_content = json.loads(resp.text)

                if len(service_obj.origins) > 0:
                    policy_content['rules'] = []
                    for origin in service_obj.origins:
                        self._process_new_origin(origin,
                                                 policy_content['rules'])
                # referrer restriction implementaiton for akamai
                # get a list of referrer restriction domains/hosts
                referrer_restriction_list = [rule.referrer
                                             for restriction in
                                             service_obj.restrictions
                                             for rule in restriction.rules]

                if any(referrer_restriction_list):
                    referrer_blacklist_value = ''.join(
                        ['*%s*' % referrer for referrer
                         in referrer_restriction_list
                         if referrer is not None])
                    for rule in policy_content['rules']:
                        self._process_referrer_restriction(
                            referrer_blacklist_value, rule)

                # post new policies back with Akamai Policy API
                try:
                    LOG.info('Start to update policy %s ' % policy)
                    resp = self.policy_api_client.put(
                        self.policy_api_base_url.format(
                            policy_name=policy),
                        data=json.dumps(policy_content),
                        headers=self.request_header)
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    LOG.info('Update policy %s complete' % policy)
                except Exception:
                    return self.responder.failed("failed to update service")
            ids = policies
            links.append({'href': self.driver.akamai_access_url_link,
                          'rel': 'access_url'})
        return self.responder.updated(json.dumps(ids), links)

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
                resp = self.policy_api_client.delete(
                    self.policy_api_base_url.format(policy_name=policy))
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
