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
            referrer_whitelist_value = ''.join(['*%s*' % referrer
                                                for referrer
                                                in referrer_restriction_list
                                                if referrer is not None])
            for rule in post_data['rules']:
                self._process_referrer_restriction(referrer_whitelist_value,
                                                   rule)

        # implementing caching-rules for akamai
        # we do not have to use copy here, since caching is only used once
        caching_rules = service_obj.caching
        # Traverse existing rules list to add caching rules necessarys
        self._process_caching_rules(caching_rules, post_data['rules'])

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
                # TODO(tonytan4ever): also classify domains based on their
                # protocols. http and https domains needs to be created
                # with separate base urls.
                configuration_number = None
                if classified_domain.protocol == 'http':
                    configuration_number = self.driver.http_conf_number
                elif classified_domain.protocol == 'https':
                    configuration_number = self.driver.https_conf_number
                resp = self.policy_api_client.put(
                    self.policy_api_base_url.format(
                        configuration_number=configuration_number,
                        policy_name=dp),
                    data=json.dumps(post_data),
                    headers=self.request_header)
                LOG.info('akamai response code: %s' % resp.status_code)
                LOG.info('akamai response text: %s' % resp.text)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)

                dp_obj = {'policy_name': dp,
                          'protocol': classified_domain.protocol}
                ids.append(dp_obj)
                # TODO(tonytan4ever): leave empty links for now
                # may need to work with dns integration
                LOG.info('Creating policy %s on domain %s complete' %
                         (dp, classified_domain.domain))
                provider_access_url = None
                if classified_domain.protocol == 'http':
                    provider_access_url = self.driver.akamai_access_url_link
                elif classified_domain.protocol == 'https':
                    provider_access_url = '.'.join(
                        [dp, self.driver.akamai_https_access_url_suffix])
                links.append({'href': provider_access_url,
                              'rel': 'access_url',
                              'domain': dp
                              })
        except Exception:
            return self.responder.failed("failed to create service")
        else:
            return self.responder.created(json.dumps(ids), links)

    def _classify_domains(self, domains_list):
        # classify domains into different categories based on first two level
        # of domains, group them together
        # for right now we just use the whole domain as the digital property
        return domains_list

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

        if origin.ssl:
            rule_dict_template['matches'].append({
                'name': 'url-scheme',
                'value': 'HTTPS'
            })
        origin_behavior_dict['params']['originDomain'] = (
            origin.origin
        )
        rule_dict_template['behaviors'].append(
            origin_behavior_dict
        )
        # Append the new generated rules
        rules_list.append(rule_dict_template)

    def _process_new_domain(self, domain, rules_list):
        dp = domain.domain

        for rule in rules_list:
            for behavior in rule['behaviors']:
                if 'params' in behavior:
                    behavior['params']['digitalProperty'] = dp
        return dp

    def _process_referrer_restriction(self, referrer_whitelist_value, rule):
        rule['behaviors'].append({
            'name': 'referer-whitelist',
            'value': referrer_whitelist_value
        })

    def _process_caching_rules(self, caching_rules, rules_list):
        for caching_rule in caching_rules:
            if caching_rule.name.lower() == 'default':
                for rule in rules_list:
                    # this branch could not be hit when there is no
                    # 'default' origin rule
                    matches_dict = rule['matches'][0]
                    if (matches_dict['name'] == 'url-wildcard' or
                        matches_dict['name'] == 'url-path') and (
                       matches_dict['value'] == '/*'):
                        rule['behaviors'].append({
                            'name': 'caching',
                            'type': 'fixed',
                            # assuming the input number to caching rule
                            # ttl is in second
                            'value': '%ss' % caching_rule.ttl
                        })
                        caching_rules.remove(caching_rule)
            else:
                for rule in rules_list:
                    matches_dict = rule['matches'][0]
                    if matches_dict['name'] == 'url-wildcard':
                        for r in caching_rule.rules:
                            if r.request_url == matches_dict['value']:
                                rule['behaviors'].append({
                                    'name': 'caching',
                                    'type': 'fixed',
                                    # assuming the input number to caching rule
                                    # ttl is in second
                                    'value': '%ss' % caching_rule.ttl
                                })
                                caching_rule.rules.remove(r)
                        if caching_rule.rules == []:
                            # in this case all the rule for this caching
                            # rule has been processed
                            caching_rules.remove(caching_rule)

        # at this point, all the unprocessed rules are still left in caching
        # rules list, wee need to add separate rule for that
        for caching_rule in caching_rules:
            rule_dict_template = {
                'matches': [],
                'behaviors': []
            }
            for rule in caching_rule.rules:
                match_rule = {
                    'name': 'url-wildcard',
                    'value': rule.request_url
                }
                rule_dict_template['matches'].append(match_rule)
            rule_dict_template['behaviors'].append({
                'name': 'caching',
                'type': 'fixed',
                # assuming the input number to caching rule
                # ttl is in second
                'value': '%ss' % caching_rule.ttl
            })
            rules_list.append(rule_dict_template)
            caching_rules.remove(caching_rule)

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
            except Exception as e:
                return self.responder.failed(str(e))

        ids = []
        links = []
        if len(service_obj.domains) > 0:
            # in this case we need to copy
            # and tweak the content of one old policy
            # and creates new policy for the new domains,
            # old policies ought to be deleted.
            try:
                configuration_number = None
                if policies[0]['protocol'] == 'http':
                    configuration_number = self.driver.http_conf_number
                elif policies[0]['protocol'] == 'https':
                    configuration_number = self.driver.https_conf_number
                resp = self.policy_api_client.get(
                    self.policy_api_base_url.format(
                        configuration_number=configuration_number,
                        policy_name=policies[0]['policy_name']),
                    headers=self.request_header)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)
            except Exception as e:
                return self.responder.failed(str(e))
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
                referrer_whitelist_value = ''.join(['*%s*' % referrer
                                                   for referrer
                                                   in referrer_restriction_list
                                                   if referrer is not None])
                for rule in policy_content['rules']:
                    self._process_referrer_restriction(
                        referrer_whitelist_value, rule)

            # implementing caching-rules for akamai
            # we do not have to use copy here, since caching is only used once
            caching_rules = service_obj.caching
            # Traverse existing rules list to add caching rules necessarys
            self._process_caching_rules(caching_rules, policy_content['rules'])

            # Update domain if necessary ( by adjust digital property)
            classified_domains = self._classify_domains(service_obj.domains)

            try:
                for classified_domain in classified_domains:
                    # assign the content realm to be the digital property field
                    # of each group
                    dp = self._process_new_domain(classified_domain,
                                                  policy_content['rules'])

                    configuration_number = None
                    if classified_domain.protocol == 'http':
                        configuration_number = self.driver.http_conf_number
                    elif classified_domain.protocol == 'https':
                        configuration_number = self.driver.https_conf_number

                    # verify the same policy
                    policy_names = [policy['policy_name'] for policy
                                    in policies]

                    # Only if a same domain with a same protocol
                    # do we need to update a existing policy
                    if dp in policy_names and (
                            policies[policy_names.index(dp)]['protocol'] == (
                            classified_domain.protocol)):
                        # in this case we should update existing policy
                        # instead of create a new policy
                        LOG.info('Start to update policy %s' % dp)
                        # TODO(tonytan4ever): also classify domains based on
                        # their protocols. http and https domains needs to be
                        # created  with separate base urls.
                        resp = self.policy_api_client.put(
                            self.policy_api_base_url.format(
                                configuration_number=(
                                    self.driver.http_conf_number),
                                policy_name=dp),
                            data=json.dumps(policy_content),
                            headers=self.request_header)
                        dp_obj = {'policy_name': dp,
                                  'protocol': classified_domain.protocol}
                        policies.remove(dp_obj)
                    else:
                        LOG.info('Start to create new policy %s' % dp)
                        resp = self.policy_api_client.put(
                            self.policy_api_base_url.format(
                                configuration_number=(
                                    configuration_number),
                                policy_name=dp),
                            data=json.dumps(policy_content),
                            headers=self.request_header)
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                    dp_obj = {'policy_name': dp,
                              'protocol': classified_domain.protocol}
                    ids.append(dp_obj)
                    # TODO(tonytan4ever): leave empty links for now
                    # may need to work with dns integration
                    LOG.info('Creating/Updateing policy %s on domain %s '
                             'complete' % (dp, classified_domain.domain))
                    provider_access_url = None
                    if classified_domain.protocol == 'http':
                        provider_access_url = (
                            self.driver.akamai_access_url_link)
                    elif classified_domain.protocol == 'https':
                        provider_access_url = '.'.join(
                            [dp, self.driver.akamai_https_access_url_suffix])
                    links.append({'href': provider_access_url,
                                  'rel': 'access_url',
                                  'domain': dp
                                  })
            except Exception:
                return self.responder.failed("failed to update service")

            try:
                for policy in policies:
                    configuration_number = None
                    if policy["protocol"] == 'http':
                        configuration_number = self.driver.http_conf_number
                    elif policy["protocol"] == 'https':
                        configuration_number = self.driver.https_conf_number

                    LOG.info('Starting to delete old policy %s' %
                             policy['policy_name'])
                    resp = self.policy_api_client.delete(
                        self.policy_api_base_url.format(
                            configuration_number=configuration_number,
                            policy_name=policy['policy_name']))
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                    LOG.info('Delete old policy %s complete' %
                             policy['policy_name'])
            except Exception:
                return self.responder.failed("failed to update service")

        else:
            # in this case we only need to adjust the existing policies
            for policy in policies:
                try:
                    configuration_number = None
                    if policy["protocol"] == 'http':
                        configuration_number = self.driver.http_conf_number
                    elif policy["protocol"] == 'https':
                        configuration_number = self.driver.https_conf_number

                    resp = self.policy_api_client.get(
                        self.policy_api_base_url.format(
                            configuration_number=configuration_number,
                            policy_name=policy['policy_name']),
                        headers=self.request_header)
                    if resp.status_code != 200:
                        raise RuntimeError(resp.text)
                except Exception as e:
                    return self.responder.failed(str(e))
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
                    referrer_whitelist_value = ''.join(
                        ['*%s*' % referrer for referrer
                         in referrer_restriction_list
                         if referrer is not None])
                    for rule in policy_content['rules']:
                        self._process_referrer_restriction(
                            referrer_whitelist_value, rule)

                # implementing caching-rules for akamai
                caching_rules = service_obj.caching
                # Traverse existing rules list to add caching rules necessarys
                self._process_caching_rules(caching_rules,
                                            policy_content['rules'])

                # post new policies back with Akamai Policy API
                try:
                    LOG.info('Start to update policy %s ' % policy)
                    resp = self.policy_api_client.put(
                        self.policy_api_base_url.format(
                            configuration_number=configuration_number,
                            policy_name=policy['policy_name']),
                        data=json.dumps(policy_content),
                        headers=self.request_header)
                    LOG.info('akamai response code: %s' % resp.status_code)
                    LOG.info('akamai response text: %s' % resp.text)
                    LOG.info('Update policy %s complete' %
                             policy['policy_name'])
                except Exception:
                    return self.responder.failed("failed to update service")
                provider_access_url = None
                if policy['protocol'] == 'http':
                    provider_access_url = (
                        self.driver.akamai_access_url_link)
                elif policy['protocol'] == 'https':
                    provider_access_url = '.'.join(
                        [dp, self.driver.akamai_https_access_url_suffix])
                links.append({'href': provider_access_url,
                              'rel': 'access_url',
                              'domain': policy['policy_name']
                              })
            ids = policies
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
            except Exception as e:
                return self.responder.failed(str(e))
        try:
            for policy in policies:
                LOG.info('Starting to delete policy %s' % policy)
                # TODO(tonytan4ever): needs to look at if service
                # domain is an https domain, if it is then a different
                # base url is needed
                configuration_number = None
                if policy["protocol"] == 'http':
                    configuration_number = self.driver.http_conf_number
                elif policy["protocol"] == 'https':
                    configuration_number = self.driver.https_conf_number

                resp = self.policy_api_client.delete(
                    self.policy_api_base_url.format(
                        configuration_number=configuration_number,
                        policy_name=policy['policy_name']))
                LOG.info('akamai response code: %s' % resp.status_code)
                LOG.info('akamai response text: %s' % resp.text)
                if resp.status_code != 200:
                    raise RuntimeError(resp.text)
        except Exception as e:
            return self.responder.failed(str(e))
        else:
            return self.responder.deleted(provider_service_id)

    def purge(self, provider_service_id, purge_url=None):
        try:
            # Get the service
            if purge_url is None:
                raise RuntimeError('Akamai purge-all functionality has not'
                                   ' been implemented')
            else:
                try:
                    policies = json.loads(provider_service_id)
                except Exception:
                    # raise a more meaningful error for debugging info
                    try:
                        raise RuntimeError('Mal-formed Akaimai policy ids: %s'
                                           % provider_service_id)
                    except Exception as e:
                        return self.responder.failed(str(e))

                for policy in policies:
                    url_scheme = None
                    if policy['protocol'] == 'http':
                        url_scheme = 'http://'
                    elif policy['protocol'] == 'https':
                        url_scheme = 'https://'

                    actual_purge_url = '.'.join([url_scheme,
                                                 policy['policy_name'],
                                                 purge_url])
                    data = {
                        'objects': [
                            actual_purge_url
                        ]
                    }
                    resp = self.ccu_api_client.post(self.ccu_api_base_url,
                                                    data=json.dumps(data),
                                                    headers=(
                                                        self.request_header
                                                    ))
                    if resp.status_code != 201:
                        raise RuntimeError(resp.text)
                return self.responder.purged(provider_service_id,
                                             purge_url=purge_url)
        except Exception as e:
            return self.responder.failed(str(e))

    @decorators.lazy_property(write=False)
    def current_customer(self):
        return None
