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


class TestSSLCDN(base.TestBase):

    """Tests for CDN enabling with SSL on."""

    def setUp(self):
        super(TestSSLCDN, self).setUp()

        if self.test_config.run_ssl_tests is False:
            self.skipTest('SSL tests are currently disabled in configuration')

        self.stack_name = self._random_string()
        self.test_domain = 'TestCDN-SSL' + self._random_string()
        self.origin = self.test_config.ssl_origin

    def test_shared_ssl_enable_cdn(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain, "protocol": "https",
                        "certificate": "shared"}]
        origin_list = [{"origin": self.origin, "port": 443, "ssl": True}]
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
        origin_url = 'http://' + self.origin
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']
        cdn_url = 'https://' + access_url[0]

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_url)

        # Benchmark page load metrics for the CDN enabled website
        if self.test_config.webpagetest_enabled:
            wpt_test_results = self.run_webpagetest(
                url=access_url, locations=self.wpt_config.test_locations)
            print(wpt_test_results)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        super(TestSSLCDN, self).tearDown()
