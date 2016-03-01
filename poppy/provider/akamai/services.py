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

import datetime
import json
import traceback

try:  # pragma: no cover
    import six.moves.urllib.parse as parse
except ImportError:  # pragma: no cover
    import urllib.parse as parse

from oslo_log import log

from poppy.common import decorators
from poppy.common import util
from poppy.provider.akamai import geo_zone_code_mapping
from poppy.provider import base

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
    def san_info_storage(self):
        return self.driver.san_info_storage

    @property
    def mod_san_queue(self):
        return self.driver.mod_san_queue

    @property
    def san_cert_cnames(self):
        return self.driver.san_cert_cnames

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.policy_api_base_url = self.driver.akamai_policy_api_base_url
        self.ccu_api_base_url = self.driver.akamai_ccu_api_base_url
        self.sps_api_base_url = self.driver.akamai_sps_api_base_url
        self.request_header = {'Content-type': 'application/json',
                               'Accept': 'text/plain'}
        self.san_cert_hostname_limit = self.driver.san_cert_hostname_limit

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
            domains_certificate_status = {}
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
                edge_host_name = None
                if classified_domain.certificate == 'san':
                    cert_info = getattr(classified_domain, 'cert_info', None)
                    if cert_info is None:
                        domains_certificate_status[
                            classified_domain.domain] = "create_in_progress"
                        continue
                    else:
                        edge_host_name = (
                            classified_domain.cert_info.get_san_edge_name())
                        domains_certificate_status[classified_domain.domain] \
                            = (classified_domain.cert_info.get_cert_status())
                        if edge_host_name is None:
                            continue
                provider_access_url = self._get_provider_access_url(
                    classified_domain, dp, edge_host_name)
                links.append({'href': provider_access_url,
                              'rel': 'access_url',
                              'domain': classified_domain.domain,
                              'certificate': classified_domain.certificate
                              })
        except Exception as e:
            LOG.exception('Creating policy failed: %s' %
                          traceback.format_exc())

            return self.responder.failed(
                "failed to create service - %s" % str(e))
        else:
            LOG.info("ids : {0} for service_id {1}".format(json.dumps(ids),
                     service_obj.service_id))
            LOG.info("links : {0} for service_id {1}".format(links,
                     service_obj.service_id))
            LOG.info("domain certificate status : {0} "
                     "for service_id {1}".format(domains_certificate_status,
                                                 service_obj.service_id))
            return self.responder.created(
                json.dumps(ids), links,
                domains_certificate_status=domains_certificate_status)

    def get(self, service_name):
        pass

    def update(self, provider_service_id,
               service_obj):
        return self._policy(provider_service_id, service_obj)

    def _policy(self, provider_service_id, service_obj,
                invalidate=False, invalidate_url=None):
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
                    msg = 'Mal-formed Akamai ' \
                          'policy ids: {0}'.format(provider_service_id)
                    LOG.exception(msg)
                    raise RuntimeError(msg)
                except Exception as e:
                    return self.responder.failed(str(e))

            ids = []
            links = []
            domains_certificate_status = {}
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
            if invalidate:
                self._process_cache_invalidation_rules(
                    invalidate_url, policy_content['rules'])
            # Update domain if necessary (by adjust digital property)
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
                                    configuration_number),
                                policy_name=dp),
                            data=json.dumps(policy_content),
                            headers=self.request_header)

                        for policy in policies:
                            # policies are based on domain_name
                            # will be unique within a provider
                            if policy['policy_name'] == dp:
                                dp_obj = policy
                                break

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
                    edge_host_name = None
                    if classified_domain.certificate == 'san':
                        cert_info = getattr(classified_domain, 'cert_info',
                                            None)
                        if cert_info is None:
                            domains_certificate_status[
                                classified_domain.domain] = (
                                    "create_in_progress")
                            continue
                        else:
                            edge_host_name = (
                                classified_domain.cert_info.
                                get_san_edge_name())
                            domains_certificate_status[
                                classified_domain.domain] = (
                                classified_domain.cert_info.get_cert_status())
                            if edge_host_name is None:
                                continue
                    provider_access_url = self._get_provider_access_url(
                        classified_domain, dp, edge_host_name)
                    links.append({'href': provider_access_url,
                                  'rel': 'access_url',
                                  'domain': dp,
                                  'certificate':
                                  classified_domain.certificate
                                  })
            except Exception:
                LOG.exception("Failed to Update Service - {0}".
                              format(provider_service_id))
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
                LOG.exception("Failed to Update Service - {0}".
                              format(provider_service_id))
                return self.responder.failed("failed to update service")
            LOG.info("ids : {0} for service_id {1}".format(json.dumps(ids),
                     service_obj.service_id))
            LOG.info("links : {0} for service_id {1}".format(links,
                     service_obj.service_id))
            LOG.info("domain certificate status : {0} "
                     "for service_id {1}".format(domains_certificate_status,
                                                 service_obj.service_id))
            return self.responder.updated(
                json.dumps(ids), links,
                domains_certificate_status=domains_certificate_status)

        except Exception as e:
            LOG.exception("Failed to Update Service - {0}".
                          format(provider_service_id))
            LOG.exception('Updating policy failed: %s', traceback.format_exc())

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
                msg = 'Mal-formed Akamai ' \
                      'policy ids: {0}'.format(provider_service_id)
                LOG.exception(msg)
                raise RuntimeError(msg)
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
            LOG.exception("Failed to Delete Service - {0}".
                          format(provider_service_id))
            return self.responder.failed(str(e))
        else:
            LOG.info("Sucessfully Deleted Service - {0}".
                     format(provider_service_id))
            return self.responder.deleted(provider_service_id)

    def purge(self, provider_service_id, service_obj, hard=True,
              purge_url='/*'):
        if not hard:
            if not purge_url.startswith('/'):
                purge_url = ('/' + purge_url)
            return self._policy(provider_service_id, service_obj,
                                invalidate=True, invalidate_url=purge_url)
        else:
            try:

                # Get the service
                if purge_url == '/*':
                    raise RuntimeError('Akamai purge-all functionality has not'
                                       ' been implemented')
                else:
                    try:
                        policies = json.loads(provider_service_id)
                    except Exception:
                        # raise a more meaningful error for debugging info
                        try:
                            msg = 'Mal-formed Akamai ' \
                                  'policy ids: {0}'.format(provider_service_id)
                            LOG.exception(msg)
                            raise RuntimeError(msg)
                        except Exception as e:
                            return self.responder.failed(str(e))

                    for policy in policies:
                        url_scheme = None
                        if policy['protocol'] == 'http':
                            url_scheme = 'http://'
                        elif policy['protocol'] == 'https':
                            url_scheme = 'https://'

                        # purge_url has to be a full path
                        # with a starting slash,
                        # e.g: /cdntest.html
                        if not purge_url.startswith('/'):
                            purge_url = ('/' + purge_url)
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
                LOG.exception("Failed to Purge/Invalidate Service - {0}".
                              format(provider_service_id))
                return self.responder.failed(str(e))

    def create_certificate(self, cert_obj, enqueue=True):
        if cert_obj.cert_type == 'san':
            try:
                if enqueue:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': 'San cert request for %s has been enqueued' %
                                  (cert_obj.domain_name)
                    })

                for san_cert_name in self.san_cert_cnames:
                    lastSpsId = (
                        self.san_info_storage.get_cert_last_spsid(
                            san_cert_name
                        )
                    )
                    if lastSpsId not in [None, ""]:
                        LOG.info('Latest spsId for %s is: %s' % (san_cert_name,
                                                                 lastSpsId))
                        resp = self.sps_api_client.get(
                            self.sps_api_base_url.format(spsId=lastSpsId),
                        )
                        if resp.status_code != 200:
                            raise RuntimeError('SPS API Request Failed'
                                               'Exception: %s' % resp.text)
                        sps_request_info = json.loads(resp.text)[
                            'requestList'][0]
                        status = sps_request_info['status']
                        workFlowProgress = sps_request_info['workflowProgress']
                        if status == 'edge host already created or pending':
                            if workFlowProgress is not None and \
                                    'error' in workFlowProgress.lower():
                                LOG.info("SPS Pending with Error:" %
                                         workFlowProgress)
                                continue
                            else:
                                pass
                        elif status == 'CPS cancelled':
                            pass
                        elif status != 'SPS Request Complete':
                            LOG.info("SPS Not completed for %s..." %
                                     san_cert_name)
                            continue
                    # issue modify san_cert sps request
                    cert_info = self.san_info_storage.get_cert_info(
                        san_cert_name)
                    cert_info['add.sans'] = cert_obj.domain_name
                    string_post_data = '&'.join(
                        ['%s=%s' % (k, v) for (k, v) in cert_info.items()])
                    LOG.info('Post modSan request with request data: %s' %
                             string_post_data)
                    resp = self.sps_api_client.post(
                        self.sps_api_base_url.format(spsId=""),
                        data=string_post_data.encode('utf-8')
                    )
                    if resp.status_code != 202:
                        raise RuntimeError('SPS Request failed.'
                                           'Exception: %s' % resp.text)
                    else:
                        resp_dict = json.loads(resp.text)
                        LOG.info('modSan request submitted. Response: %s' %
                                 str(resp_dict))
                        this_sps_id = resp_dict['spsId']
                        self.san_info_storage.save_cert_last_spsid(
                            san_cert_name,
                            this_sps_id)
                        return self.responder.ssl_certificate_provisioned(
                            san_cert_name, {
                                'status': 'create_in_progress',
                                'san cert': san_cert_name,
                                'akamai_spsId': this_sps_id,
                                'created_at': str(datetime.datetime.now()),
                                'action': 'Waiting for customer domain '
                                          'validation for %s' %
                                          (cert_obj.domain_name)
                            })
                else:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': 'No available san cert for %s right now,'
                                  ' or no san cert info available. Support:'
                                  'Please write down the domain and keep an'
                                  ' eye on next availabe freed-up SAN certs.'
                                  ' More provisioning might be needed' %
                                  (cert_obj.domain_name)
                    })
            except Exception as e:
                LOG.exception(e)
                return self.responder.ssl_certificate_provisioned(None, {
                    'status': 'failed',
                    'san cert': None,
                    'created_at': str(datetime.datetime.now()),
                    'action': 'Waiting for action... '
                              'Provision san cert failed for %s failed.' %
                              cert_obj.domain_name
                })
        else:
            return self.responder.ssl_certificate_provisioned(None, {
                'status': 'failed',
                'reason': 'Cert type : %s hasn\'t been implemented'
            })

    @decorators.lazy_property(write=False)
    def current_customer(self):
        return None

    def _classify_domains(self, domains_list):
        # classify domains into different categories based on first two level
        # of domains, group them together
        # for right now we just use the whole domain as the digital property
        return domains_list

    def _process_new_origin(self, origin, rules_list):

        # NOTE(TheSriram): ensure that request_url starts with a '/'
        for rule in origin.rules:
            if rule.request_url:
                if not rule.request_url.startswith('/'):
                    rule.request_url = ('/' + rule.request_url)

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

        if origin.hostheadertype == 'custom':
            origin_behavior_dict['params']['hostHeaderType'] = 'fixed'
            origin_behavior_dict['params']['hostHeaderValue'] = \
                origin.hostheadervalue
        elif origin.hostheadertype == 'origin':
            origin_behavior_dict['params']['hostHeaderType'] = 'origin'
            origin_behavior_dict['params']['hostHeaderValue'] = \
                origin.hostheadervalue

        wildcards = []

        # this is the global 'url-wildcard' rule
        if origin.rules == []:
            wildcards.append("/*")
        else:
            for rule in origin.rules:
                wildcards.append(rule.request_url)

        if len(wildcards) > 0:
            match_rule = {
                'name': 'url-wildcard',
                'value': " ".join(wildcards)
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
        dp = domain.domain

        for rule in rules_list:
            for behavior in rule['behaviors']:
                if 'params' in behavior:
                    behavior['params']['digitalProperty'] = dp
        return dp

    def _process_restriction_rules(self, restriction_rules, rules_list):

        # NOTE(TheSriram): ensure that request_url starts with a '/'
        for restriction_rule in restriction_rules:
            for rule_entry in restriction_rule.rules:
                if rule_entry.request_url:
                    if not rule_entry.request_url.startswith('/'):
                        rule_entry.request_url = (
                            '/' + rule_entry.request_url)
        # restriction implementation for akamai
        # for each restriction rule

        # restriction entities include: referrer, geography, client_ip
        restriction_entities = ['referrer', 'geography', 'client_ip']

        class entityRequestUrlMappingList(dict):

            """A dictionary with a name attribute"""

            def __init__(self, name, orig_dict):
                self.name = name
                self.update(orig_dict)

        # classify restriction/rules based on their white/black-list
        white_list_entities = entityRequestUrlMappingList(
            'whitelist',
            {entity: {} for entity
             in restriction_entities})
        black_list_entities = entityRequestUrlMappingList(
            'blacklist',
            {entity: {} for entity
             in restriction_entities})

        for restriction_rule in restriction_rules:
            entity_rule_mapping = {}
            if restriction_rule.access == 'whitelist':
                entity_rule_mapping = white_list_entities
            elif restriction_rule.access == 'blacklist':
                entity_rule_mapping = black_list_entities
            for rule_entry in restriction_rule.rules:
                # classify rules based on their entities, then request_urls
                if getattr(rule_entry, "referrer", None) is not None:
                    if (rule_entry.request_url not in
                            entity_rule_mapping['referrer']):
                        entity_rule_mapping['referrer'][rule_entry.request_url]\
                            = [rule_entry]
                    else:
                        entity_rule_mapping['referrer'][rule_entry.request_url]\
                            .append(rule_entry)
                elif getattr(rule_entry, "client_ip", None) is not None:
                    if (rule_entry.request_url not in
                            entity_rule_mapping['client_ip']):
                        entity_rule_mapping['client_ip'][rule_entry.request_url]\
                            = [rule_entry]
                    else:
                        entity_rule_mapping['client_ip'][rule_entry.request_url]\
                            .append(rule_entry)
                elif getattr(rule_entry, "geography", None) is not None:
                    if (rule_entry.request_url not in
                            entity_rule_mapping['geography']):
                        entity_rule_mapping['geography'][rule_entry.request_url]\
                            = [rule_entry]
                    else:
                        entity_rule_mapping['geography'][rule_entry.request_url]\
                            .append(rule_entry)

        for entity_request_url_rule_mapping in [white_list_entities,
                                                black_list_entities]:
            for entity in entity_request_url_rule_mapping:
                for request_url in entity_request_url_rule_mapping[entity]:
                    found_match = False
                    # need to write up a function gets the value of behavior
                    behavior_name = self._get_behavior_name(
                        entity, entity_request_url_rule_mapping.name)

                    behavior_value = self._get_behavior_value(
                        entity,
                        entity_request_url_rule_mapping[entity][request_url])

                    behavior_dict = {
                        'name': behavior_name,
                        'value': behavior_value
                    }

                    if entity == 'geography':
                        behavior_dict['type'] = 'country'

                    # if we have a matches rule already
                    for rule in rules_list:
                        for match in rule['matches']:
                            if request_url == match['value']:
                                # we found an existing matching rule.
                                # add the whitelist/blacklist behavior to it
                                found_match = True

                                rule['behaviors'].append(behavior_dict)

                    # if there is no matches entry yet for this rule
                    if not found_match:
                        # create an akamai rule
                        rule_dict_template = {
                            'matches': [],
                            'behaviors': []
                        }

                        # add the match and behavior to this new rule
                        if rule_entry.request_url is not None:
                            match_rule = {
                                'name': 'url-wildcard',
                                'value': request_url
                            }

                            rule_dict_template['matches'].append(match_rule)
                            rule_dict_template['behaviors'].append(
                                behavior_dict)
                            rules_list.append(rule_dict_template)
                # end loop - request url
            # end loop - entity

    def _process_cache_invalidation_rules(self, invalidation_url,
                                          rules_list):
        found_match = False
        # if we have a matches rule already
        for rule in rules_list:
            for match in rule['matches']:
                if invalidation_url == match['value']:
                    # we found an existing matching rule.
                    # add the cache invalidation behavior to it
                    found_match = True
                    rule['behaviors'].append({
                        'name': 'content-refresh',
                        'type': 'natural',
                        'value': 'now',
                    })
        # if there is no matches entry yet for this rule
        if not found_match:
            # create an akamai rule
            rule_dict_template = {
                'matches': [],
                'behaviors': []
            }
            # add the match and behavior to this new rule
            match_rule = {
                'name': 'url-wildcard',
                'value': invalidation_url
            }
            rule_dict_template['matches'].append(match_rule)
            rule_dict_template['behaviors'].append({
                'name': 'content-refresh',
                'type': 'natural',
                'value': 'now',
            })
            rules_list.append(rule_dict_template)

    def _get_behavior_name(self, entity, entity_restriction_access):
        prefix = suffix = None
        if entity == 'referrer':
            prefix = 'referer'
        elif entity == 'client_ip':
            prefix = 'ip'
        elif entity == 'geography':
            prefix = 'geo'

        if entity_restriction_access == 'whitelist':
            suffix = 'whitelist'
        elif entity_restriction_access == 'blacklist':
            suffix = 'blacklist'

        return '-'.join([prefix, suffix])

    def _get_behavior_value(self, entity, rule_entries):
        if entity == 'referrer':
            return ' '.join(
                ['*%s*' % referrer
                 for rule_entry
                 in rule_entries
                 for referrer
                 in rule_entry.referrer.split()
                 ])
        elif entity == 'client_ip':
            return ' '.join(
                ['%s' % rule_entry.client_ip
                 for rule_entry
                 in rule_entries
                 ])
        elif entity == 'geography':
            # We ignore the country that Akamai doesn't support for right now
            zones_list = []
            for rule_entry in rule_entries:
                if rule_entry.geography in (
                        geo_zone_code_mapping.REGION_COUNTRY_MAPPING):
                    zones_list.extend(
                        geo_zone_code_mapping.REGION_COUNTRY_MAPPING[
                            rule_entry.geography])
                else:
                    zones_list.append(rule_entry.geography)
            # NOTE(tonytan4ever):Too many country code to check and maybe more
            # countries in the future, so put in checking duplicates logic here
            country_code_list = [
                '%s' %
                geo_zone_code_mapping.COUNTRY_CODE_MAPPING.get(zone, '')
                for zone in zones_list
                if geo_zone_code_mapping.COUNTRY_CODE_MAPPING.get(zone, '')
                != '']
            if len(country_code_list) > len(set(country_code_list)):
                raise ValueError("Duplicated country code in %s" %
                                 str(country_code_list))
            res = ' '.join(country_code_list)
            return res

    def _process_caching_rules(self, caching_rules, rules_list):
        # akamai requires all caching rules to start with '/'
        # so, if a caching rules does not start with '/'
        # prefix the caching rule with '/'
        for caching_rule in caching_rules:
            for caching_rule_entry in caching_rule.rules:
                if not caching_rule_entry.request_url.startswith('/'):
                    caching_rule_entry.request_url = (
                        '/' + caching_rule_entry.request_url)

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
                            if caching_rule.ttl == 0:
                                # NOTE(TheSriram): if ttl is set zero,
                                # we directly serve content from origin and do
                                # not cache the content on edge server.
                                rule['behaviors'].append({
                                    'name': 'caching',
                                    'type': 'no-store',
                                    'value': '%ss' % caching_rule.ttl
                                })
                            else:
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
                    match_rule = {
                        'name': 'url-wildcard',
                        'value': caching_rule_entry.request_url
                    }

                    rule_dict_template['matches'].append(match_rule)
                    if caching_rule.ttl == 0:
                        # NOTE(TheSriram): if ttl is set zero,
                        # we directly serve content from origin and do
                        # not cache the content on edge server.
                        rule_dict_template['behaviors'].append({
                            'name': 'caching',
                            'type': 'no-store',
                            'value': '%ss' % caching_rule.ttl
                        })
                    else:
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
            if domain_obj.certificate == 'shared':
                configuration_number = self.driver.https_shared_conf_number
            elif domain_obj.certificate == 'san':
                configuration_number = self.driver.https_san_conf_number
            elif domain_obj.certificate == 'custom':
                configuration_number = self.driver.https_custom_conf_number
            else:
                raise ValueError("Unknown certificate type: %s" %
                                 domain_obj.certificate)
        return configuration_number

    def _get_provider_access_url(self, domain_obj, dp, edge_host_name=None):
        provider_access_url = None
        if domain_obj.protocol == 'http':
            provider_access_url = self.driver.akamai_access_url_link
        elif domain_obj.protocol == 'https':
            if domain_obj.certificate == "shared":
                provider_access_url = '.'.join(
                    ['.'.join(dp.split('.')[1:]),
                     self.driver.akamai_https_access_url_suffix])
            elif domain_obj.certificate == 'san':
                if edge_host_name is None:
                    raise ValueError("No EdgeHost name provided for SAN Cert")
                # ugly fix for existing san cert domains, but we will
                # have to take it for now
                elif edge_host_name.endswith(
                        self.driver.akamai_https_access_url_suffix):
                    provider_access_url = edge_host_name
                else:
                    provider_access_url = '.'.join(
                        [edge_host_name,
                         self.driver.akamai_https_access_url_suffix])
            elif domain_obj.certificate == 'custom':
                provider_access_url = '.'.join(
                    [dp, self.driver.akamai_https_access_url_suffix])
            else:
                raise ValueError("Unknown certificate type: %s" %
                                 domain_obj.certificate)
        return provider_access_url

    def _pick_san_edgename(self):
        """Inspect && Pick a SAN cert cnameHostname for this user.

        Based on what the date is it current date, pick a san cert
        """
        find_idx = (
            datetime.datetime.today().weekday() % len(self.san_cert_cnames))

        return self.san_cert_cnames[find_idx]

    def get_provider_service_id(self, service_obj):
        id_list = []
        for domain in service_obj.domains:
            dp_obj = {'policy_name': domain.domain,
                      'protocol': domain.protocol,
                      'certificate': domain.certificate}
            id_list.append(dp_obj)
        return json.dumps(id_list)

    def get_metrics_by_domain(self, project_id, domain_name, regions,
                              **extras):
        """Use Akamai's report API to get the metrics by domain."""

        formatted_results = dict()
        metric_buckets = []
        metricType = extras['metricType']
        startTime = extras['startTime']
        endTime = extras['endTime']
        metrics_controller = extras['metrics_controller']
        resolution = self.driver.metrics_resolution
        if 'httpResponseCode' in metricType:
            http_series = metricType.split('_')[1]
            for region in regions:
                metric_buckets.append('_'.join(['requestCount', domain_name,
                                                region,
                                                http_series]))
        else:
            for region in regions:
                metric_buckets.append('_'.join([metricType, domain_name,
                                                region]))

        metrics_results = metrics_controller.read(metric_names=metric_buckets,
                                                  from_timestamp=startTime,
                                                  to_timestamp=endTime,
                                                  resolution=resolution)

        formatted_results['domain'] = domain_name
        formatted_results[metricType] = dict()

        for region in regions:
            formatted_results[metricType][region] = []
            for metric_name, metrics_response in metrics_results:
                unquoted_metric_name = parse.unquote(
                    metric_name.split('_')[2]
                ).lower()
                if region.lower() == unquoted_metric_name:
                    formatted_results[metricType][region].append(
                        metrics_response
                    )

        return formatted_results
