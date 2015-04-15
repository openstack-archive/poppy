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
import time

from bs4 import BeautifulSoup
from cafe.drivers.unittest import fixtures
import cafe.engine.http.client as cafe_client
import requests

from tests.api.utils import client
from tests.endtoend.utils import config
from tests.endtoend.utils import dnsclient
from tests.endtoend.utils import heatclient
from tests.endtoend.utils import wptclient


def random_string(prefix, n=10):
    return prefix + ''.join([random.choice('1234567890') for _ in xrange(n)])


class TestBase(fixtures.BaseTestFixture):
    """Base class for End To End CDN Tests

    The tests do the following,
    1. Spins up a wordpress site on a cloud server.
    2. Create a Poppy service via API call using the origin & domain
        feom Step 1.
    3. Measures the pageload performance of the CDN enabled website.
    """

    @classmethod
    def setUpClass(cls):

        super(TestBase, cls).setUpClass()

        # use http_client.get (not requests.get) to have requests logged
        cls.http_client = cafe_client.HTTPClient()

        cls.auth_config = config.AuthConfig()
        cls.auth_client = client.AuthClient()
        auth_token, project_id = cls.auth_client.authenticate_user(
            cls.auth_config.base_url,
            cls.auth_config.user_name,
            cls.auth_config.api_key)

        cls.test_config = config.TestConfig()
        cls.poppy_config = config.PoppyConfig()

        if cls.poppy_config.project_id_in_url:
            cls.url = cls.poppy_config.base_url + '/v1.0/' + project_id
        else:
            cls.url = cls.poppy_config.base_url + '/v1.0'

        cls.poppy_client = client.PoppyClient(
            cls.url, auth_token, project_id,
            serialize_format='json',
            deserialize_format='json')

        cls.dns_config = config.DNSConfig()
        cls.dns_client = dnsclient.RackspaceDNSClient(
            user_name=cls.auth_config.user_name,
            api_key=cls.auth_config.api_key,
            test_domain=cls.dns_config.test_domain)

        cls.heat_config = config.OrchestrationConfig()
        heat_url = cls.heat_config.base_url + '/' + project_id
        cls.heat_client = heatclient.HeatClient(heat_url=heat_url,
                                                token=auth_token)

        cls.wpt_config = config.WebPageTestConfig()
        cls.wpt_client = wptclient.WebpageTestClient(
            wpt_url=cls.wpt_config.base_url, api_key=cls.wpt_config.api_key)

    def get_content(self, url):
        """Get content from the url

        :param url: url to get content from
        :returns: content fetched from the url
        """
        response = requests.get(url)
        content = BeautifulSoup(response.text)
        return content.findAll()

    def assertSameContent(self, origin_url, cdn_url):
        """Asserts that the origin & access_url serve the same content

        :param origin: Origin website
        :param cdn_url: CDN enabled url of the origin website
        :returns: True/False
        """
        origin_content = self.get_content(url=origin_url)
        cdn_content = self.get_content(url=cdn_url)
        self.assertEqual(origin_content, cdn_content)

    def setup_cname(self, name, cname):
        """Create a CNAME record and wait for propagation."""
        cname_rec = self.dns_client.add_cname_rec(name=name, data=cname)

        start = time.time()
        # if we query caching nameservers and get an NXDOMAIN, that NXDOMAIN
        # will then be cached for five minutes.
        #
        # In order to avoid this five minute wait, don't query the caching
        # nameservers. Hit the authoritative nameserver(s) directly until
        # the name shows up.
        self.dns_client.wait_cname_propagation(
            target=name,
            nameserver=self.dns_config.nameserver,
            retry_interval=self.dns_config.retry_interval,
            retry_timeout=self.dns_config.retry_timeout)
        print("waited {0} seconds to propagate to authoritive nameserver {1}"
              .format(time.time() - start, self.dns_config.nameserver))

        # once the name is on the authoritative nameserver, there will still be
        # a delay for the name to propagate out to the caching nameservers
        sleep_time = 30
        print("waiting {0} additional seconds to propagate to caching "
              "nameservers".format(sleep_time))
        time.sleep(sleep_time)

        return cname_rec

    def setup_service(self, service_name, domain_list, origin_list,
                      caching_list=[], restrictions_list=[], flavor_id=None):
        resp = self.poppy_client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            restrictions_list=restrictions_list,
            flavor_id=flavor_id)

        self.assertEqual(resp.status_code, 202)
        self.service_location = resp.headers['location']
        self.poppy_client.wait_for_service_status(
            location=self.service_location,
            status='DEPLOYED',
            abort_on_status='FAILED',
            retry_interval=self.poppy_config.status_check_retry_interval,
            retry_timeout=self.poppy_config.status_check_retry_timeout)

        return resp

    def run_webpagetest(self, url):
        """Runs webpagetest

        :param url: URL to gather metrics on
        :returns: test_result_location
        """
        wpt_test_results = {}
        for location in self.wpt_config.test_locations:
            wpt_test_url = self.wpt_client.start_test(test_url=url,
                                                      test_location=location,
                                                      runs=2)
            wpt_test_results[location] = wpt_test_url
            self.wpt_client.wait_for_test_status(status='COMPLETE',
                                                 test_url=wpt_test_url)
            wpt_test_results[location] = self.wpt_client.get_test_details(
                test_url=wpt_test_url)
        return wpt_test_results

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
