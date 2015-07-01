# coding= utf-8

# Copyright (c) 2015 Rackspace, Inc.
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

import ddt
import random

from tests.api import base


@ddt.ddt
class TestSanCertService(base.TestBase):

    def setUp(self):
        super(TestSanCertService, self).setUp()

        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='api-test-domain') + '.com'
        self.domain_list = [
            {"domain": domain, "protocol": "https", "certificate": "san"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 443,
                u"ssl": True,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": domain,
                        u"referrer": domain,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]

    def test_migrate(self):
        new_certs = self.san_certs_config.certs
        index = random.randint(0, len(new_certs)-1)
        new_cert = new_certs[index]
        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = get_resp_body['domains'][0]['domain']
        resp = self.client.admin_migrate_domain(
            project_id=self.user_project_id, service_id=get_resp_body['id'],
            domain=domain, new_cert=new_cert)
        self.assertEqual(resp.status_code, 202)

        new_resp = self.client.get_service(location=self.service_url)
        new_resp_body = new_resp.json()

        for link in new_resp_body['links']:
            if link['rel'] == 'access_url':
                access_url = link['href']

        suffix = self.dns_config.url
        data = self.dns_client.verify_domain_migration(access_url=access_url,
                                                       suffix=suffix)
        # Akamai specific suffix
        if not new_cert.endswith("edgekey.net"):
            new_cert = new_cert + ".edgekey.net"

        self.assertEqual(data, new_cert)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestSanCertService, self).tearDown()
