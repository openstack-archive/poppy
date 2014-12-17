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


class RackspaceDNSClient(object):

    """Client Objects for Rackspace DNS call."""

    def __init__(self, user_name, api_key, test_domain):
        super(RackspaceDNSClient, self).__init__()

        pyrax.settings.set('identity_type', 'rackspace')
        pyrax.set_credentials(user_name, api_key)
        self.dns_client = pyrax.cloud_dns
        self.test_domain = test_domain
        self.domain = self.dns_client.find(name=test_domain)

    def create_sub_domain(self, sub_domain, email, ttl=300,
                          comment='TestDomain'):
        """Create Sub domain

        :param email: email id to use
        :param ttl: time to live
        :param comment: comment for sub domain
        :returns sub_domain
        """
        self.sub_domain = sub_domain + '.' + self.test_domain

        domain = self.dns_client.create(
            name=self.sub_domain, emailAddress=email, ttl=ttl, comment=comment)
        return domain.name

    def add_a_rec(self, domain_name, ip, ttl=300):
        """Add A Record

        :param ip: ip
        :param domain_name: domain to which the A record will be added
        :param ttl: ttl
        :returns recs
        """
        a_rec = {"type": "A",
                 "name": self.test_domain,
                 "data": ip,
                 "ttl": ttl}

        recs = self.domain.add_records([a_rec])
        return recs

    def add_cname_rec(self, name, data, ttl=300, comment="TestCNAMERecord"):
        """Adds CNAME record
        """
        import ipdb; ipdb.set_trace()
        c_name_rec = {"type": "CNAME",
                      "name": name,
                      "data": data,
                      "ttl": ttl,
                      "comment": comment}
        recs = self.domain.add_records([c_name_rec])
        return recs

    def delete_record(self, record):
        """Deletes record

        :param record: record
        :returns: delete response
        """
        recs = self.domain.delete_record(record)
        return recs
