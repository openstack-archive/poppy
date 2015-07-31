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

import urlparse
import uuid

import ddt

from tests.api import base


@ddt.ddt
class TestHttpsInLinkService(base.TestBase):

    """Tests if pagination links use http URLs"""

    def _create_test_service(self):
        service_name = str(uuid.uuid1())

        self.domain_list = [{"domain": self.generate_random_string(
            prefix='www.security-test-domain') + '.com'}]

        self.origin_list = [{"origin": self.generate_random_string(
            prefix='security-test-origin') + '.com', "port": 80, "ssl": False,
            "hostheadertype": "custom", "hostheadervalue":
            "www.seccustomweb.com"}]

        self.caching_list = []
        self.log_delivery = {"enabled": False}

        resp = self.client.create_service(service_name=service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          log_delivery=self.log_delivery)

        self.service_url = resp.headers["location"]
        self.service_list.append(self.service_url)

        self._check_https_in_location_header(self.service_url)
        return self.service_url

    def _check_http_not_in_links(self, body):
        """Make sure plain http: is not used in links"""

        num_links = len(body['links'])
        for i in range(num_links):
            href = body['links'][i]['href']
            self.assertNotEqual(href[0:5], 'http:')

        num_links = len(body['services'][0]['links'])
        for i in range(num_links):
            if body['services'][0]['links'][i]['rel'] == 'self':
                href = body['services'][0]['links'][i]['href']
                self.assertNotEqual(href[0:5], 'http:')

    def _check_https_in_location_header(self, location_url):
        self.assertTrue(
            location_url.startswith('https://'),
            msg="{0} should start with 'https://'.".format(location_url)
        )

    def _cleanup_test_data(self):
        for service in self.service_list:
            self.client.delete_service(location=service)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

    def setUp(self):
        super(TestHttpsInLinkService, self).setUp()

        if self.test_config.run_https_link_tests is False:
            self.skipTest(
                'Test secure HTTPS links Functions is '
                'disabled in configuration'
            )

        self.addCleanup(self._cleanup_test_data)
        self.service_list = []
        self.flavor_id = self.test_flavor

    @ddt.data(3)
    def test_https_in_links(self, num):
        for _ in range(num):
            self._create_test_service()

        url_param = {'limit': 1}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(len(body['services']), 1)
        self._check_http_not_in_links(body)

        # get second page
        next_page_uri = urlparse.urlparse(body['links'][0]['href'])
        marker = urlparse.parse_qs(next_page_uri.query)['marker'][0]
        url_param = {'marker': marker, 'limit': 1}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(len(body['services']), 1)
        self._check_http_not_in_links(body)

        # get third page
        next_page_uri = urlparse.urlparse(body['links'][0]['href'])
        marker = urlparse.parse_qs(next_page_uri.query)['marker'][0]
        url_param = {'marker': marker, 'limit': 1}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(len(body['services']), 1)
        self._check_http_not_in_links(body)

    def tearDown(self):
        self._cleanup_test_data()
        super(TestHttpsInLinkService, self).tearDown()
