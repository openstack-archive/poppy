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

from tests.endtoend import base


class TestWebsiteCDN(base.TestBase):

    """Tests for CDN enabling a website."""

    def setUp(self):
        super(TestWebsiteCDN, self).setUp()

        sub_domain = base.random_string(prefix='test-cdn-')
        self.test_domain = sub_domain + '.' + self.dns_config.test_domain

        self.origin = self.test_config.default_origin
        self.cname_rec = []

    def test_enable_cdn(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
        self.service_name = base.random_string(prefix='e2e-cdn-')

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(name=self.test_domain, cname=access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url, cdn_url=cdn_enabled_url)

        if self.test_config.webpagetest_enabled:
            self.run_webpagetest(url=cdn_enabled_url)

    def test_multiple_domains(self):

        # Create another domain in addition to the one created in setUp
        sub_domain2 = base.random_string(prefix='test-cdn-')
        self.test_domain2 = sub_domain2 + '.' + self.dns_config.test_domain

        # Create a Poppy Service for the test website with two domains
        domain_list = [{"domain": self.test_domain},
                       {"domain": self.test_domain2}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
        self.service_name = base.random_string(prefix='e2e-cdn-')

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        # Adds cname records corresponding to the test domains
        rec = self.setup_cname(name=self.test_domain, cname=access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        rec = self.setup_cname(name=self.test_domain2, cname=access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        origin_url = 'http://' + self.origin
        cdn_enabled_url1 = 'http://' + self.test_domain
        cdn_enabled_url2 = 'http://' + self.test_domain2

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url1)

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url2)

        if self.test_config.webpagetest_enabled:
            wpt_result_1 = self.run_webpagetest(url=cdn_enabled_url1)
            wpt_result_2 = self.run_webpagetest(url=cdn_enabled_url2)
            print(wpt_result_1)
            print(wpt_result_2)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            print("deleting dns record: {0}".format(record))
            self.dns_client.delete_record(record)
        super(TestWebsiteCDN, self).tearDown()
