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

import requests

from tests.endtoend import base


class TestReferrerRestriction(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestReferrerRestriction, cls).setUpClass()

        cls.test_domain = cls.dns_config.test_domain
        cls.referree_origin = cls.test_config.referree_origin

    def setUp(self):
        super(TestReferrerRestriction, self).setUp()
        self.referree_domain = "{0}.{1}".format(
            base.random_string("referree"), self.test_domain)
        self.service_name = base.random_string("ReferrerRestrictionService")

    def test_referrer_restriction(self):
        domains = [{'domain': self.referree_domain}]
        origins = [{
            "origin": self.referree_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        restrictions = [{
            "name": "restriction",
            "rules": [{
                "name": "my site",
                "referrer": self.referree_domain,
            }]
        }]

        self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        self.setup_cname(self.referree_domain, access_url[0])

        cdn_url = "http://" + self.referree_domain

        # fetching from a whitelisted referrer should work
        resp = requests.get(cdn_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 200)

        # fetching from a restriction domain should not work
        resp = requests.get(cdn_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 403)

        # fetching with no referrer should work
        resp = requests.get(cdn_url)
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestReferrerRestriction, self).tearDown()
