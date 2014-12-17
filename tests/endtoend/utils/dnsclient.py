# coding= utf-8

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

import pyrax


class DNSClient(object):

    """Client Objects for Rackspace DNS call."""

    def __init__(self, user_name, api_key, test_domain):
        super(DNSClient, self).__init__()

        pyrax.settings.set('identity_type', 'rackspace')
        pyrax.set_credentials(user_name, api_key)
        self.dns_client = pyrax.cloud_dns
        self.test_domain = test_domain
        self.domain = self.dns_client.find(name=test_domain)

    def create_sub_domain(self, sub_domain, email, ttl=300,
                          comment='TestDomain'):
        """Create Sub domain

        :param email:
        :param ttl:
        :param comment:
        :returns sub_domain
        """
        self.sub_domain = sub_domain + '.' + self.test_domain

        domain = self.dns_client.create(
            name=self.sub_domain, emailAddress=email, ttl=ttl, comment=comment)
        return domain.name

    def add_a_rec(self, domain_name, ip, ttl=6000):
        """Add A Record

        :param ip:
        :param domain_name:
        :param ttl:
        :returns recs:
        """
        a_rec = {"type": "A",
                 "name": self.test_domain,
                 "data": ip,
                 "ttl": ttl}

        #import ipdb; ipdb.set_trace()
        recs = self.domain.add_records([a_rec])
        return recs
