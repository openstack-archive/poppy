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
try:
    set
except NameError:  # noqa  pragma: no cover
    from sets import Set as set  # noqa  pragma: no cover

import pyrax.exceptions as exc

from poppy.dns import base
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


class ServicesController(base.ServicesBase):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.client = driver.client

    def _get_subdomain(self, subdomain_name):
        """Returns a subdomain, if it does not exist, create it

        :param subdomain_name
        :return subdomain
        """

        try:
            subdomain = self.client.find(name=subdomain_name)
        except exc.NotFound:
            subdomain = self.client.create(
                name=subdomain_name,
                emailAddress=self._driver.rackdns_conf.email,
                ttl=900)
        return subdomain

    def _create_cname_records(self, links):
        """Creates a subdomain

        :param links: Access URLS from providers
        :return dns_links: Map from provider access URL to DNS access URL
        """

        cdn_domain_name = self._driver.rackdns_conf.url
        shard_prefix = self._driver.rackdns_conf.shard_prefix
        num_shards = self._driver.rackdns_conf.num_shards

        # randomly select a shard
        shard_id = random.randint(1, num_shards)
        subdomain_name = '{0}{1}.{2}'.format(shard_prefix, shard_id,
                                             cdn_domain_name)
        subdomain = self._get_subdomain(subdomain_name)
        # create CNAME record for adding
        cname_records = []
        dns_links = {}
        for link in links:
            name = '{0}.{1}'.format(link, subdomain_name)
            cname_record = {'type': 'CNAME',
                            'name': name,
                            'data': links[link],
                            'ttl': 300}
            dns_links[links[link]] = name
            cname_records.append(cname_record)
        # add the cname records
        subdomain.add_records(cname_records)
        return dns_links

    def _delete_cname_record(self, access_url):
        """Delete a CNAME record

        :param access_url: DNS Access URL
        :return error_msg: returns error message, if any
        """

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
            return error_msg
        return

    def create(self, responders):
        """Create CNAME record for a service.

        :param responders: responders from providers
        :return dns_links: Map from provider urls to DNS urls
        """
        # gather the provider urls and cname them
        links = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                for link in responder[provider_name]['links']:
                    if link['rel'] == 'access_url':
                        links[link['domain']] = link['href']

        if not links:
            return self.responder.created({})

        # create CNAME records
        try:
            dns_links = self._create_cname_records(links)
        except Exception as e:
            error_msg = 'Rackspace DNS Exception: {0}'.format(e)
            LOG.error(error_msg)
            return self.responder.failed(error_msg)

        # gather the CNAMED links
        dns_details = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                access_urls = []
                for link in responder[provider_name]['links']:
                    if link['rel'] == 'access_url':
                        access_url = {
                            'domain': link['domain'],
                            'provider_url': link['href'],
                            'operator_url': dns_links[link['href']]}
                        access_urls.append(access_url)
                dns_details[provider_name] = {'access_urls': access_urls}
        return self.responder.created(dns_details)

    def delete(self, provider_details):
        """Delete CNAME records for a service.

        :param provider_details
        :return dns_details: Map from provider_name to delete errors
        """

        dns_details = {}
        for provider_name in provider_details:
            error_msg = ''
            access_urls = provider_details[provider_name].access_urls
            for access_url in access_urls:
                try:
                    msg = self._delete_cname_record(access_url['operator_url'])
                    if msg:
                        error_msg = error_msg + msg
                except exc.NotFound as e:
                    LOG.error('Can not access the subdomain. Please make sure'
                              ' it exists and you have permissions to CDN '
                              'subdomain {0}'.format(e))
                    error_msg = (error_msg + 'Can not access subdomain . '
                                 'Exception: {0}'.format(e))
                except Exception as e:
                    LOG.error('Exception: {0}'.format(e))
                    error_msg = error_msg + 'Exception: {0}'.format(e)
            # format the error or success message for this provider
            if error_msg:
                dns_details[provider_name] = self.responder.failed(error_msg)
            else:
                dns_details[provider_name] = self.responder.deleted({})
        return dns_details

    def _update_added_domains(self, responders, added_domains):
        """Update added domains."""

        # if no domains are added, return
        dns_details = {}
        if not added_domains:
            for responder in responders:
                for provider_name in responder:
                    dns_details[provider_name] = {'access_urls': {}}
            return dns_details

        # gather the provider links for the added domains
        links = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                for link in responder[provider_name]['links']:
                    domain_added = (link['rel'] == 'access_url' and
                                    link['domain'] in added_domains)
                    if domain_added:
                        links[link['domain']] = link['href']

        # create CNAME records for added domains
        try:
            dns_links = self._create_cname_records(links)
        except Exception as e:
            error_msg = 'Rackspace DNS Exception: {0}'.format(e)
            LOG.error(error_msg)
            return self.responder.failed(error_msg)

        # gather the CNAMED links for added domains
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                access_urls = {}
                for link in responder[provider_name]['links']:
                    if link['domain'] in added_domains:
                        access_urls[link['href']] = dns_links[link['href']]
                dns_details[provider_name] = {'access_urls': access_urls}
        return dns_details

    def _update_removed_domains(self, provider_details, removed_domains):
        """Update removed domains."""

        # if no domains are removed, return
        dns_details = {}
        if not removed_domains:
            for provider_name in provider_details:
                dns_details[provider_name] = {'access_urls': {}}
            return dns_details

        # delete the records for deleted domains
        for provider_name in provider_details:
            error_msg = ''
            provider_detail = provider_details[provider_name]
            for access_url in provider_detail.access_urls:
                if access_url['domain'] not in removed_domains:
                    continue
                try:
                    msg = self._delete_cname_record(access_url['operator_url'])
                    if msg:
                        error_msg = error_msg + msg
                except exc.NotFound as e:
                    LOG.error('Can not access the subdomain. Please make sure'
                              ' it exists and you have permissions to CDN '
                              'subdomain {0}'.format(e))
                    error_msg = (error_msg + 'Can not access subdomain. '
                                 'Exception: {0}'.format(e))
                except Exception as e:
                    LOG.error('Exception: {0}'.format(e))
                    error_msg = error_msg + 'Exception: {0}'.format(e)
            # format the error or success message for this provider
            if error_msg:
                dns_details[provider_name] = self.responder.failed(error_msg)
            else:
                dns_details[provider_name] = self.responder.deleted({})
        return dns_details

    def update(self, service_old, service_updates, responders):
        """Update CNAME records for a service.

        :param service_old: previous service state
        :param service_updates: updates to service state
        :param responders: responders from providers

        :return dns_details: Map from provider_name to update errors
        """

        # get old domains
        old_domains = set()
        old_access_urls_map = {}
        provider_details = service_old.provider_details
        for provider_name in provider_details:
            provider_detail = provider_details[provider_name]
            access_urls = provider_detail.access_urls
            old_access_urls_map[provider_name] = {'access_urls': access_urls}
            for access_url in access_urls:
                old_domains.add(access_url['domain'])

        # if there is a provider error, don't try dns update
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    return old_access_urls_map

        # get new_domains
        new_domains = set()
        for responder in responders:
            for provider_name in responder:
                links = responder[provider_name]['links']
                for link in links:
                    new_domains.add(link['domain'])

        # if domains have not been updated, return
        if not service_updates.domains:
            return old_access_urls_map

        # if the old set of domains is the same as new set of domains, return
        if old_domains == new_domains:
            return old_access_urls_map

        # get the list of added, removed and common domains
        added_domains = new_domains.difference(old_domains)
        removed_domains = old_domains.difference(new_domains)
        common_domains = new_domains.intersection(old_domains)

        # add new domains
        dns_links = self._update_added_domains(responders, added_domains)

        # remove CNAME records for deleted domains
        provider_details = service_old.provider_details
        self._update_removed_domains(provider_details, removed_domains)

        # gather the CNAMED links and remove stale links
        dns_details = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                provider_detail = service_old.provider_details[provider_name]
                old_access_urls = provider_detail.access_urls
                operator_urls = dns_links[provider_name]['access_urls']
                access_urls = []
                for link in responder[provider_name]['links']:
                    if link['domain'] in removed_domains:
                        continue
                    elif link['domain'] in added_domains:
                        operator_url = operator_urls[link['href']]
                        access_url = {
                            'domain': link['domain'],
                            'provider_url': link['href'],
                            'operator_url': operator_url}
                        access_urls.append(access_url)
                    elif link['domain'] in common_domains:
                        # iterate through old access urls and get access url
                        operator_url = None
                        for old_access_url in old_access_urls:
                            if old_access_url['domain'] == link['domain']:
                                operator_url = old_access_url['operator_url']
                                break
                        access_url = {
                            'domain': link['domain'],
                            'provider_url': link['href'],
                            'operator_url': operator_url}
                        access_urls.append(access_url)
                dns_details[provider_name] = {'access_urls': access_urls}

        return self.responder.updated(dns_details)
