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

import hashlib
import random
import traceback

import pyrax.exceptions as exc

from poppy.dns import base


class ServicesController(base.ServicesBase):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.client = driver.client

    def update(self):
        return

    def delete(self, provider_details, responder):
        for provider_name in provider_details:
            provider_detail = provider_details[provider_name]
            for access_url in provider_detail.access_urls:
                # extract shard name: make sure there is no exception here
                shard_name = access_url.split('.')[-3]
                # TODO(obulpathi): make sure shard name is valid
                subdomain_name = '.'.join([shard_name, self._driver.rackdns_conf.url])
                # get subdomain
                try:
                    subdomain = self.client.find(name=subdomain_name)
                except exc.NotFound:
                    LOG.error('Can not access the domain. Please make sure it exists'
                        'and you have permissions to CDN domain')
                    raise Exception('An internal error occured')
                except Exception as e:
                    LOG.error('Rackspace DNS Exception: {0}'.format(e))
                    raise Exception('An internal error occured')
                # delete the CNAME record
                name = access_url
                record_type = 'CNAME'
                records = self.client.search_records(subdomain, record_type, name)
                # we should get just one record
                if len(records) != 1:
                    raise Exception('No record or multiple records found: {0}'.format(access_url))
                records[0].delete()
        return responder

    def create(self, responders):
        cdn_domain_name = self._driver.rackdns_conf.url
        shard_prefix = self._driver.rackdns_conf.shard_prefix
        num_shards = self._driver.rackdns_conf.num_shards

        # randomly select a shard
        shard_id = random.randint(0, num_shards-1)
        # TODO(obulpathi): remove this, this is just for debugging
        shard_id = 0
        subdomain_name = '{0}{1}.{2}'.format(shard_prefix, shard_id,
            cdn_domain_name)

        # get subdomain
        try:
            subdomain = self.client.find(name=subdomain_name)
        except exc.NotFound:
            LOG.error('Can not access the domain. Please make sure it exists'
                'and you have permissions to CDN domain')
            raise Exception('An internal error occured')
        except Exception as e:
            LOG.error('Rackspace DNS Exception: {0}'.format(e))
            raise Exception('An internal error occured')

        # create CNAME records
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    continue
                for link in responder[provider_name]['links']:
                    if link['rel'] == 'access_url':
                        # CNAME record for adding
                        user_domain_name = link['domain']
                        provider_domain_name = link['href']
                        rackcdn_domain_name = '{0}.{1}'.format(
                            user_domain_name, subdomain_name)
                        link['href'] = rackcdn_domain_name
                        cname_record = {'type': 'CNAME',
                                        'name': rackcdn_domain_name,
                                        'data': provider_domain_name,
                                        'ttl': 300}
                        try:
                            records = subdomain.add_records([cname_record])
                        except Exception as e:
                            error_msg = 'Rackspace DNS Exception: {0}'.format(e)
                            error_detail = traceback.format_exc()
                            LOG.error(error_msg)
                            LOG.error(error_detail)
                            responder[provider_name]['error'] = error_msg
                            responder[provider_name]['error_detail'] = error_detail
                            continue

        return responders
