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

import random
import string

from tests.endtoend import base


class TestWebsiteCDN(base.TestBase):

    """Tests for CDN enabling a website."""

    def _random_string(self, length=12):
        return ''.join([random.choice(string.ascii_letters)
                        for _ in range(length)])

    def setUp(self):
        super(TestWebsiteCDN, self).setUp()

        sub_domain = 'TestCDN-' + self._random_string()
        self.test_domain = sub_domain + '.' + self.dns_config.test_domain

        print('Domain Name', self.test_domain)

        self.origin = self.test_config.wordpress_origin

    def test_enable_cdn(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
        self.service_name = 'testService-' + self._random_string()

        resp = self.poppy_client.create_service(
            service_name=self.service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_id=self.poppy_config.flavor)

        self.assertEqual(resp.status_code, 202)
        self.service_location = resp.headers['location']
        self.poppy_client.wait_for_service_status(
            location=self.service_location,
            status='DEPLOYED',
            abort_on_status='FAILED',
            retry_interval=self.poppy_config.status_check_retry_interval,
            retry_timeout=self.poppy_config.status_check_retry_timeout)

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']
        self.cname_rec = self.dns_client.add_cname_rec(
            name=self.test_domain, data=access_url[0])

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.dns_client.wait_cname_propagation(
            target=self.test_domain,
            retry_interval=self.dns_config.retry_interval)

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url)

        # Benchmark page load metrics for the CDN enabled website
        if self.test_config.webpagetest_enabled:
            wpt_test_results = {}
            for location in self.wpt_config.test_locations:
                wpt_test_url = self.wpt_client.start_test(
                    test_url=cdn_enabled_url, test_location=location, runs=2)
                wpt_test_results[location] = wpt_test_url
                self.wpt_client.wait_for_test_status(
                    status='COMPLETE', test_url=wpt_test_url)
                wpt_test_results[location] = self.wpt_client.get_test_details(
                    test_url=wpt_test_url)

            print('Webpage Tests Results', wpt_test_url)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        # self.dns_client.delete_record(self.cname_rec)
        super(TestWebsiteCDN, self).tearDown()
