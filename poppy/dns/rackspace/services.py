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
import traceback

import pyrax.exceptions as exc

from poppy.dns import base
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


class ServicesController(base.ServicesBase):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.client = driver.client

    def _get_subdomain(self, subdomain_name):
        # get subdomain; if it does not exist, create it
        try:
            subdomain = self.client.find(name=subdomain_name)
        except exc.NotFound:
            subdomain = self.client.create(
                name=subdomain_name,
                emailAddress=self.client.rackdns_conf.email,
                ttl=900)
        return subdomain

    def _create_cname_record(self, data, domain, dns_details):
        cdn_domain_name = self._driver.rackdns_conf.url
        shard_prefix = self._driver.rackdns_conf.shard_prefix
        num_shards = self._driver.rackdns_conf.num_shards

        # randomly select a shard
        shard_id = random.randint(0, num_shards - 1)
        subdomain_name = '{0}{1}.{2}'.format(shard_prefix, shard_id,
                                             cdn_domain_name)
        subdomain = self._get_subdomain(subdomain_name)
        # CNAME record for adding
        name = '{0}.{1}'.format(domain, subdomain_name)
        cname_record = {'type': 'CNAME',
                        'name': name,
                        'data': data,
                        'ttl': 300}
        subdomain.add_records([cname_record])

    def _delete_cname_record(self, access_url):
        # extract shard name
        shard_name = access_url.split('.')[-3]
        subdomain_name = '.'.join([shard_name, self._driver.rackdns_conf.url])
        # get subdomain
        subdomain = self.client.find(name=subdomain_name)
        # search and find the CNAME record
        name = access_url
        record_type = 'CNAME'
        records = self.client.search_records(subdomain, record_type, name)
        # delete the record
        # we should get one record,
        # or none if it has been deleted already
        if not records:
            LOG.info('DNS record already deleted: {0}'.format(access_url))
        elif len(records) == 1:
            LOG.info('Deleting DNS records for : {0}'.format(access_url))
            records[0].delete()
        elif len(records) > 1:
            error_msg = 'Multiple DNS records found: {0}'.format(access_url)
            return error
        return

    def update(self):
        return

    def delete(self, provider_details):
        dns_details = {}
        for provider_name in provider_details:
            error_msg = ''
            provider_detail = provider_details[provider_name]
            for provider_url in provider_detail.access_urls:
                access_url = provider_detail.access_urls[provider_url]
                try:
                    # extract shard name
                    shard_name = access_url.split('.')[-3]
                    subdomain_name = '.'.join([shard_name,
                                               self._driver.rackdns_conf.url])
                    # get subdomain
                    subdomain = self.client.find(name=subdomain_name)
                    # search and find the CNAME record
                    name = access_url
                    record_type = 'CNAME'
                    records = self.client.search_records(subdomain,
                                                         record_type, name)
                    # delete the record
                    # we should get one record,
                    # or none if it has been deleted already
                    if not records:
                        LOG.info('DNS records were already deleted: {0}'
                                 .format(access_url))
                    elif len(records) == 1:
                        LOG.info('Deleting DNS records for : {0}'
                                 .format(access_url))
                        records[0].delete()
                    elif len(records) > 1:
                        error_msg = (error_msg + 'Multiple DNS records found: '
                                     '{0}'.format(access_url))
                except exc.NotFound as e:
                    LOG.error('Can not access the subdomain. Please make sure'
                              ' it exists and you have permissions to CDN '
                              'subdomain {0}'.format(e))
                    error_msg = (error_msg + 'Can not access subdomain {0}. '
                        'Exception: {1}'.format(subdomain_name, e))
                except Exception as e:
                    LOG.error('Exception: {0}'.format(e))
                    error_msg = error_msg + 'Exception: {0}'.format(e)
            # format the error or success message for this provider
            if error_msg:
                dns_details[provider_name] = self.responder.failed(error_msg)
            else:
                dns_details[provider_name] = self.responder.deleted({})
        return dns_details

    def create(self, responders):
        dns_details = {}
        cdn_domain_name = self._driver.rackdns_conf.url
        shard_prefix = self._driver.rackdns_conf.shard_prefix
        num_shards = self._driver.rackdns_conf.num_shards

        # randomly select a shard
        shard_id = random.randint(0, num_shards - 1)
        subdomain_name = '{0}{1}.{2}'.format(shard_prefix, shard_id,
                                             cdn_domain_name)

        # get subdomain; if it does not exist, create it
        try:
            subdomain = self.client.find(name=subdomain_name)
        except exc.NotFound:
            try:
                subdomain = self.client.create(
                    name=subdomain_name,
                    emailAddress=self.client.rackdns_conf.email,
                    ttl=900)
            except Exception as e:
                LOG.error(u'Rackspace DNS: Can not create subdomain. {0}'
                          .format(e))
                for responder in responders:
                    for provider_name in responder:
                        dns_details[provider_name] = self.responder.failed(
                            'An internal error occured')
                return dns_details
        except Exception as e:
            LOG.error('Rackspace DNS Exception: {0}'.format(e))
            for responder in responders:
                for provider_name in responder:
                    dns_details[provider_name] = self.responder.failed(
                        'An internal error occured')
            return dns_details

        # create CNAME records
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                provider_links = {}
                dns_details[provider_name] = {}
                for link in responder[provider_name]['links']:
                    if link['rel'] == 'access_url':
                        # CNAME record for adding
                        user_domain_name = link['domain']
                        provider_domain_name = link['href']
                        rackcdn_domain_name = '{0}.{1}'.format(
                            user_domain_name, subdomain_name)
                        cname_record = {'type': 'CNAME',
                                        'name': rackcdn_domain_name,
                                        'data': provider_domain_name,
                                        'ttl': 300}

                        try:
                            subdomain.add_records([cname_record])
                        except Exception as e:
                            error_msg = ('Rackspace DNS Exception: {0}'
                                         .format(e))
                            error_detail = traceback.format_exc()
                            LOG.error(error_msg)
                            LOG.error(error_detail)
                            dns_details[provider_name] = self.responder.failed(
                                error_msg)
                            continue
                        provider_links[provider_domain_name] = (
                            rackcdn_domain_name)
                    dns_details[provider_name]['access_urls'] = provider_links

        return self.responder.created(dns_details)
