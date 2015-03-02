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

import copy
import json
import traceback

from poppy.common import decorators
from poppy.common import util
from poppy.openstack.common import log
from poppy.provider.akamai import utils
from poppy.provider import base

# to use log inside worker, we need to directly use logging
LOG = log.getLogger(__name__)


class ServiceController(base.ServiceBase):

    @property
    def policy_api_client(self):
        return self.driver.policy_api_client

    @property
    def ccu_api_client(self):
        return self.driver.ccu_api_client

    @property
    def sps_api_client(self):
        return self.driver.akamai_sps_api_client

    @property
    def papi_api_client(self):
        return self.driver.akamai_papi_api_client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.policy_api_base_url = self.driver.akamai_policy_api_base_url
        self.ccu_api_base_url = self.driver.akamai_ccu_api_base_url
        self.sps_api_base_url = self.driver.akamai_sps_api_base_url
        self.papi_api_base_url = self.driver.akamai_papi_api_base_url
        self.request_header = {'Content-type': 'application/json',
                               'Accept': 'text/plain'}

        self.san_cert_hostname_limit = (
            self.driver.akamai_conf.san_cert_hostname_limit)
        # For queue backends
        self.san_cert_add_job_backend = (
            self.driver.san_cert_add_job_backend)
        self.papi_job_update_job_backend = (
            self.driver.papi_job_update_job_backend)
        self.status_checking_job_backend = (
            self.driver.status_checking_job_backend)

    def create_custom_single_cert(self, domain):
        s_data = self._get_custom_cert_data(domain)

        resp = self.sps_api_client.post(
            self.driver.akamai_sps_api_base_url.format(spsId=""),
            data=s_data
        )
        if resp.status_code != 202:
            raise RuntimeError('SPS Request failed.'
                               'Exception: %s' % resp.text)

        resp_data = json.loads(resp.text)
        spsId = resp_data['spsId']
        jobID = resp_data['Results']['data'][0]['results']['jobID']
        return spsId, jobID

    def _get_custom_cert_data(self, domain):
        """"""
        custom_cert_data_template = {
            'cnameHostname': domain.domain,
            'issuer': 'cybertrust',
            'createType': 'single',
            'csr.cn': domain.domain,
            'csr.c': ' '.join(domain.domain_info.get(
                'registra-country', 'None').split()).replace(' ', '+'),
            'csr.st': ' '.join(domain.domain_info.get(
                'registra-state', 'None').split()).replace(' ', '+'),
            'csr.l': ' '.join(domain.domain_info.get(
                'registra-city', 'None').split()).replace(' ', '+'),
            'csr.o': ' '.join(domain.domain_info.get(
                'registra-orgainzation', 'None').split()).replace(' ', '+'),
            'csr.ou': ' '.join(domain.domain_info.get(
                'registra-industry', 'None').split()).replace(' ', '+'),
            'organization-information.organization-name':
                ' '.join(domain.domain_info.get(
                    'organization-name', 'None').split()).replace(' ', '+'),
            'organization-information.address-line-one':
                ' '.join(domain.domain_info.get(
                    'organization-address', 'None').split()).replace(' ', '+'),
            'organization-information.city':
                ' '.join(domain.domain_info.get(
                    'organization-city', 'None').split()).replace(' ', '+'),
            'organization-information.region':
                ' '.join(domain.domain_info.get(
                    'organization-region', 'None').split()).replace(' ', '+'),
            'organization-information.postal-code':
                ' '.join(domain.domain_info.get(
                    'organization-postal-code', 'None').split()).replace(' ',
                                                                         '+'),
            'organization-information.country':
                ' '.join(domain.domain_info.get(
                    'organization-country', 'None').split()).replace(' ', '+'),
            'organization-information.phone': ' '.join(domain.domain_info.get(
                'organization-phone', 'None').split()).replace(' ', '+'),
            'admin-contact.first-name': ' '.join(domain.domain_info.get(
                'admin-contact-first-name', 'None').split()).replace(' ', '+'),
            'admin-contact.last-name': ' '.join(domain.domain_info.get(
                'admin-contact-last-name', 'None').split()).replace(' ', '+'),
            'admin-contact.phone': ' '.join(domain.domain_info.get(
                'admin-contact-phone', 'None').split()).replace(' ', '+'),
            # needs to url encode the email id
            # example:zali%40akamai.com
            'admin-contact.email':
                ' '.join(domain.domain_info.get(
                    'admin-contact-email',
                    'None').split()).replace(' ', '+').replace('@', '%40'),
            'technical-contact.first-name': 'Rachita',
            'technical-contact.last-name': 'Ahanthem',
            'technical-contact.phone': '16174755662',
            'technical-contact.email': 'rahanthe%40akamai.com',
            'ipVersion': 'ipv4',
            ##################
            # 'product' : 'alta',
            'slot-deployment.klass': 'esslType'
        }

        s_data = '&'.join(['%s=%s' % (k, v) for (k, v) in
                           custom_cert_data_template.items()])
        return s_data

    def create(self, service_obj):
        try:
            post_data = {
                'rules': []
            }

            # for now global level akamai only supports 1 origin match global
            # * url. At this point we are guaranteed there is at least 1 origin
            # in incoming service_obj
            # form all origin rules for this service
            for origin in service_obj.origins:
                self._process_new_origin(origin, post_data['rules'])

            # implementing caching-rules for akamai
            # we do not have to use copy here, since caching is only used once
            # caching_rules = copy.deepcopy(service_obj.caching)

            # Traverse existing rules list to add caching rules necessarys
            self._process_caching_rules(
                service_obj.caching, post_data['rules'])
            self._process_restriction_rules(
                service_obj.restrictions, post_data['rules'])

            classified_domains = self._classify_domains(service_obj.domains)

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
                LOG.info("Creating Akamai Policy: %s", json.dumps(post_data))

                configuration_number = self._get_configuration_number(
                    classified_domain)
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
                          'protocol': classified_domain.protocol,
                          'certificate': classified_domain.certificate}
                ids.append(dp_obj)
                # TODO(tonytan4ever): leave empty links for now
                # may need to work with dns integration
                LOG.info('Creating policy %s on domain %s complete' %
                         (dp, classified_domain.domain))
                # pick a san cert for this domain
                edgeHostName = None
                if classified_domain.certificate == 'san':
                    edgeHostName = self._pick_san_edgename()
                provider_access_url = self._get_provider_access_url(
                    classified_domain, dp, edgeHostName)
                links.append({'href': provider_access_url,
                              'rel': 'access_url',
                              'domain': classified_domain.domain,
                              'certificate': classified_domain.certificate
                              })
        except Exception as e:
            LOG.error('Creating policy failed: %s' % traceback.format_exc())

            return self.responder.failed(
                "failed to create service - %s" % str(e))
        else:
            # Need to find a way to let service stay at create_in_progress
            # state
            extra = {}
            san_or_custom_domains = filter(
                lambda domain: (domain.get('certificate', None)
                                in ['san', 'custom']), ids)
            if len(list(san_or_custom_domains)) > 0:
                extra.update({
                    'status': 'create_in_progress'
                })
            return self.responder.created(json.dumps(ids), links, **extra)

    def get(self, service_name):
        pass

    def update(self, provider_service_id,
               service_obj):

        try:
            # depending on domains field presented or not, do PUT/POST
            # and depending on origins field presented or not, set behavior on
            # the data or not
            try:
                # get a list of policies
                policies = json.loads(provider_service_id)
            except Exception:
                # raise a more meaningful error for debugging info
                try:
                    raise RuntimeError('Mal-formed Akamai policy ids: %s' %
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
                    configuration_number = self._get_configuration_number(
                        util.dict2obj(policies[0]))
                    resp = self.policy_api_client.get(
                        self.policy_api_base_url.format(
                            configuration_number=configuration_number,
                            policy_name=policies[0]['policy_name']),
                        headers=self.request_header)
                    # if the policy is not found with provider, create it
                    if resp.status_code == 404:
                        LOG.info('akamai response code: %s' % resp.status_code)
                        LOG.info('upserting service with'
                                 'akamai: %s' % service_obj.service_id)
                        return self.create(service_obj)
                    elif resp.status_code != 200:
                        raise RuntimeError(resp.text)
                except Exception as e:
                    return self.responder.failed(str(e))
                else:
                    policy_content = json.loads(resp.text)
                # Update origin if necessary
                if len(service_obj.origins) > 0:
                    policy_content['rules'] = []
                    for origin in service_obj.origins:
                        self._process_new_origin(
                            origin, policy_content['rules'])

                # implementing caching-rules for akamai
                # we need deep copy since caching rules will be used in late
                # upadate objects
                # caching_rules = copy.deepcopy(service_obj.caching)
                # Traverse existing rules list to add caching rules necessarys
                self._process_caching_rules(
                    service_obj.caching, policy_content['rules'])
                self._process_restriction_rules(
                    service_obj.restrictions, policy_content['rules'])

                # Update domain if necessary ( by adjust digital property)
                classified_domains = self._classify_domains(
                    service_obj.domains)

                try:
                    for classified_domain in classified_domains:
                        # assign the content realm to be the
                        # digital property field of each group
                        dp = self._process_new_domain(classified_domain,
                                                      policy_content['rules'])

                        configuration_number = self._get_configuration_number(
                            classified_domain)

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
                            LOG.info("Updating Akamai Policy: %s",
                                     json.dumps(policy_content))

                            # TODO(tonytan4ever): also classify domains based
                            # on their protocols. http and https domains needs
                            # to be created  with separate base urls.
                            resp = self.policy_api_client.put(
                                self.policy_api_base_url.format(
                                    configuration_number=(
                                        self.driver.http_conf_number),
                                    policy_name=dp),
                                data=json.dumps(policy_content),
                                headers=self.request_header)
                            dp_obj = {'policy_name': dp,
                                      'protocol': classified_domain.protocol,
                                      'certificate':
                                      classified_domain.certificate}
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
                                  'protocol': classified_domain.protocol,
                                  'certificate': classified_domain.certificate}
                        ids.append(dp_obj)
                        # TODO(tonytan4ever): leave empty links for now
                        # may need to work with dns integration
                        LOG.info('Creating/Updating policy %s on domain %s '
                                 'complete' % (dp, classified_domain.domain))
                        edgeHostName = None
                        if classified_domain.certificate == 'san':
                            edgeHostName = self._pick_san_edgename()
                        provider_access_url = self._get_provider_access_url(
                            classified_domain, dp, edgeHostName)
                        links.append({'href': provider_access_url,
                                      'rel': 'access_url',
                                      'domain': dp,
                                      'certificate':
                                      classified_domain.certificate
                                      })
                except Exception:
                    return self.responder.failed("failed to update service")

                try:
                    for policy in policies:
                        configuration_number = self._get_configuration_number(
                            util.dict2obj(policy))

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
                        configuration_number = self._get_configuration_number(
                            util.dict2obj(policy))

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

                    # implementing caching-rules for akamai
                    caching_rules = copy.deepcopy(service_obj.caching)
                    # Traverse existing rules list to add caching rules
                    # necessarys
                    self._process_caching_rules(caching_rules,
                                                policy_content['rules'])
                    self._process_restriction_rules(
                        service_obj.restrictions, policy_content['rules'])

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
                        return self.responder.failed(
                            "failed to update service")

                    # This part may need to revisit
                    edgeHostName = None
                    if policy['certificate'] == 'san':
                        edgeHostName = self._pick_san_edgename()
                    provider_access_url = self._get_provider_access_url(
                        util.dict2obj(policy), policy['policy_name'],
                        edgeHostName)
                    links.append({'href': provider_access_url,
                                  'rel': 'access_url',
                                  'domain': policy['policy_name'],
                                  'certificate': policy['certificate']
                                  })
                ids = policies
            # Need to find a way to let service stay at create_in_progress
            # state
            extra = {}
            san_or_custom_domains = filter(
                lambda domain: (domain.get('certificate', None)
                                in ['san', 'custom']), ids)
            if len(list(san_or_custom_domains)) > 0:
                extra.update({
                    'status': 'update_in_progress'
                })
            return self.responder.updated(json.dumps(ids), links)

        except Exception as e:
            LOG.error('Updating policy failed: %s', traceback.format_exc())

            return self.responder.failed(
                "failed to update service - %s" % str(e))

    def delete(self, provider_service_id):
        # delete needs to provide a list of policy id/domains
        # then delete them accordingly
        try:
            policies = json.loads(provider_service_id)
        except Exception:
            # raise a more meaningful error for debugging info
            try:
                raise RuntimeError('Mal-formed Akamai policy ids: %s' %
                                   provider_service_id)
            except Exception as e:
                return self.responder.failed(str(e))
        try:
            for policy in policies:
                LOG.info('Starting to delete policy %s' % policy)
                # TODO(tonytan4ever): needs to look at if service
                # domain is an https domain, if it is then a different
                # base url is needed
                configuration_number = self._get_configuration_number(
                    util.dict2obj(policy))

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
                        raise RuntimeError('Mal-formed Akamai policy ids: %s'
                                           % provider_service_id)
                    except Exception as e:
                        return self.responder.failed(str(e))

                for policy in policies:
                    url_scheme = None
                    if policy['protocol'] == 'http':
                        url_scheme = 'http://'
                    elif policy['protocol'] == 'https':
                        url_scheme = 'https://'

                    # purge_url has to be a full path with a starting slash,
                    # e.g: /cdntest.html
                    actual_purge_url = ''.join([url_scheme,
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
                'cacheKeyType': 'digital_property',
                'hostHeaderValue': '-',
                'cacheKeyValue': '-'
            }
        }

        wildcards = []
        urlpaths = []

        # this is the global 'url-wildcard' rule
        if origin.rules == []:
            wildcards.append("/*")
        else:
            for rule in origin.rules:
                if "*" in rule.request_url:
                    wildcards.append(rule.request_url)
                else:
                    urlpaths.append(rule.request_url)

        if len(wildcards) > 0:
            match_rule = {
                'name': 'url-wildcard',
                'value': " ".join(wildcards)
            }

            rule_dict_template['matches'].append(
                match_rule)

        if len(urlpaths) > 0:
            match_rule = {
                'name': 'url-path',
                'value': " ".join(urlpaths)
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

    def _process_restriction_rules(self, restriction_rules, rules_list):
        # restriction implementation for akamai
        # for each restriction rule
        for restriction_rule in restriction_rules:
            for rule_entry in restriction_rule.rules:
                if rule_entry.referrer is not None:
                    found_match = False
                    referrer_whitelist_value = ' '.join(
                        ['*%s*' % referrer
                         for referrer
                         in rule_entry.referrer.split(' ')
                         ])

                    # if we have a matches rule already
                    for rule in rules_list:
                        for match in rule['matches']:
                            if rule_entry.request_url == match['value']:
                                # we found an existing matching rule.
                                # add the cache behavior to it
                                found_match = True

                                rule['behaviors'].append({
                                    'name': 'referer-whitelist',
                                    'value': referrer_whitelist_value
                                })

                    # if there is no matches entry yet for this rule
                    if not found_match:
                        # create an akamai rule
                        rule_dict_template = {
                            'matches': [],
                            'behaviors': []
                        }

                        # add the match and behavior to this new rule
                        if rule_entry.request_url is not None:
                            if "*" in rule_entry.request_url:
                                match_rule = {
                                    'name': 'url-wildcard',
                                    'value': rule_entry.request_url
                                }
                            else:
                                match_rule = {
                                    'name': 'url-path',
                                    'value': rule_entry.request_url
                                }

                            rule_dict_template['matches'].append(match_rule)
                            rule_dict_template['behaviors'].append({
                                'name': 'referer-whitelist',
                                'value': referrer_whitelist_value
                            })
                            rules_list.append(rule_dict_template)
            # end loop - restriction_rule.rules
        # end lop - restriction_rules

    def _process_caching_rules(self, caching_rules, rules_list):
        # for each caching rule
        for caching_rule in caching_rules:
            for caching_rule_entry in caching_rule.rules:
                found_match = False
                # if we have a matches rule already
                for rule in rules_list:
                    for match in rule['matches']:
                        if caching_rule_entry.request_url == match['value']:
                            # we found an existing matching rule.
                            # add the cache behavior to it
                            found_match = True
                            rule['behaviors'].append({
                                'name': 'caching',
                                'type': 'fixed',
                                # assuming the input number to caching rule
                                # ttl is in second
                                'value': '%ss' % caching_rule.ttl
                            })

                # if there is no matches entry yet for this rule
                if not found_match:
                    # create an akamai rule
                    rule_dict_template = {
                        'matches': [],
                        'behaviors': []
                    }

                    # add the match and behavior to this new rule
                    if "*" in caching_rule_entry.request_url:
                        match_rule = {
                            'name': 'url-wildcard',
                            'value': caching_rule_entry.request_url
                        }
                    else:
                        match_rule = {
                            'name': 'url-path',
                            'value': caching_rule_entry.request_url
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
            # end loop - caching_rule.rules
        # end loop - caching_rules

    def _get_configuration_number(self, domain_obj):
        # TODO(tonytan4ever): also classify domains based on their
        # protocols. http and https domains needs to be created
        # with separate base urls.
        configuration_number = None
        if domain_obj.protocol == 'http':
            configuration_number = self.driver.http_conf_number
        elif domain_obj.protocol == 'https':
            configuration_number = self.driver.https_conf_number
        return configuration_number

    def _get_provider_access_url(self, domain_obj, dp, edgeHostName=None):
        provider_access_url = None
        if domain_obj.protocol == 'http':
            provider_access_url = self.driver.akamai_access_url_link
        elif domain_obj.protocol == 'https':
            if domain_obj.certificate == "shared":
                provider_access_url = '.'.join(
                    ['.'.join(dp.split('.')[1:]),
                     self.driver.akamai_https_access_url_suffix])
            if domain_obj.certificate == 'san':
                if edgeHostName is None:
                    raise ValueError("No EdgeHost name provided for SAN Cert")
                provider_access_url = '.'.join(
                    [edgeHostName, self.driver.akamai_https_access_url_suffix])
            elif domain_obj.certificate == 'custom':
                provider_access_url = '.'.join(
                    [dp, self.driver.akamai_https_access_url_suffix])
        return provider_access_url

    def _pick_san_edgename(self):
        """Inspect && Pick a SAN cert cnameHostname for this user"""
        if self.san_cert_cnames is None or len(self.san_cert_cnames) == 0:
            raise ValueError('No valid SAN Cert has been configured. '
                             'Please check your configuration')
        find_idx = 0
        minimum_number_hosts = 2
        # Pick the san cert with the smallest number of hosts present
        # 2 will be the initial number
        for idx, san_cname in enumerate(self.san_cert_cnames):
            n = utils.get_ssl_number_of_hosts('.'.join(
                [san_cname, self.driver.akamai_https_access_url_suffix]))
            if idx == 0:
                minimum_number_hosts = n
            if n == 2:
                find_idx = idx
                break
            if n >= self.san_cert_hostname_limit:
                if idx == len(self.san_cert_cnames)-1:
                    raise ValueError('All SAN Certs are having the maximum'
                                     ' # of hostnames.Please contact operation'
                                     ' team to create more SAN Certs')
                continue

            if n < minimum_number_hosts:
                find_idx = idx
                minimum_number_hosts = n

        return self.san_cert_cnames[find_idx]

    def enqueue_add_san_cert_service(self, project_id,
                                     service_id, domain_name):
        self.san_cert_add_job_backend.put(str.encode(json.dumps(['add', (
            project_id, service_id), domain_name])))

    def enqueue_remove_san_cert_service(self, project_id, service_id):
        # We don't queu it up yet because currently there is no way
        # to remove a host from a san cert. Maybe we should just save
        # those hostnames to be deleted inside of a file
        self.san_cert_add_job_backend.put(str.encode(
            json.dumps(['remove', (project_id, service_id)])))

    def dequeue_all_add_san_cert_service(self):
        result = []
        for i in range(0, len(self.san_cert_add_job_backend)):
            i
            result.append(self.san_cert_add_job_backend.get())
            self.san_cert_add_job_backend.consume()
        return result

    def requeue_mod_san_cert_services(self, all_services):
        # ignore removed_service for right now
        self.san_cert_add_job_backend.put_all(all_services)

    def enqueue_papi_update_job(self, j_type, message, services_list_info=[]):
        valid_j_type = ['rule', 'hosts', 'hosts-remove',
                        'secureEdgeHost', 'origin-ssl-cert']
        if j_type not in valid_j_type:
            raise ValueError(
                u'PAPI Job type {0} not in valid options: {1}'.format(
                    j_type,
                    valid_j_type))
        else:
            message_dict = {
                'j_type': j_type,
                'message': message}
            # Optionally pass in a services list, to enqueue in status list
            if services_list_info != []:
                message_dict.update({
                    'services_list_info': services_list_info
                })
            self.papi_job_update_job_backend.put(json.dumps(message_dict))

    def dequeue_all_papi_jobs(self):
        result = []
        for i in range(0, len(self.papi_job_update_job_backend)):
            i
            result.append(self.papi_job_update_job_backend.get())
            self.papi_job_update_job_backend.consume()
        return result

    def requeue_papi_update_jobs(self, papi_job_list):
        self.papi_job_update_job_backend.put_all(papi_job_list)

    def enqueue_status_check_queue(self, status_check_info, services_list):
        """Enqueue a status check list job.

        :param status_check_info: a dictionary of what status to check. Now
            it supports either 'SPSStatusCheck' as a key with value of and
            spsId or 'PropertyActivation' with value to be a activation id
        :param services_list: A list of service to check those statues on
        """
        valid_check_subject = ['SPSStatusCheck', 'PropertyActivation']
        for key in status_check_info:
            if key not in valid_check_subject:
                raise ValueError(
                    u'Invalid status check subject {0}'
                    ' not in valid options: {1}'.format(
                        key,
                        valid_check_subject))
        self.status_checking_job_backend.put(str.encode(json.dumps(
            (status_check_info,
             services_list))))

    def dequeue_status_check_queue(self):
        if self.len_status_check_queue() == 0:
            return None, None
        status_check_info, services_list = json.loads((
            self.status_checking_job_backend.get()))
        self.status_checking_job_backend.consume()
        return status_check_info, services_list

    def len_status_check_queue(self):
        """Return the length of status_check_queue"""
        return len(self.status_checking_job_backend)
