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
from tests.endtoend.utils import config


class TestIpRestrictions(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestIpRestrictions, cls).setUpClass()

        cls.test_config = config.TestConfig()
        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get("http://" + cls.default_origin)

        assert origin.status_code == 200

    def setUp(self):
        super(TestIpRestrictions, self).setUp()
        self.service_name = base.random_string('E2E-IP-Restriction')
        self.cname_rec = []

        self.service_location = ''

    def get_ip_address(self):
        return requests.get('https://api.ipify.org').text

    def test_ip_blacklist(self):
        test_domain = "{0}.{1}".format(
            base.random_string('test-blacklist-ip'),
            self.dns_config.test_domain)
        domains = [{'domain': test_domain}]
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        caching = [
            {"name": "default",
             "ttl": 3600,
             "rules": [{"name": "default", "request_url": "/*"}]}]

        test_system_ip = self.get_ip_address()
        restrictions = [
            {"name": "test_ip_blacklist",
             "type": "blacklist",
             "rules": [{"name": "blacklist",
                        "client_ip": test_system_ip,
                        "request_url": "/*"}]}]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        # Verify blacklisted IP cannot fetch cdn content
        cdn_url = 'http://' + test_domain
        resp = self.http_client.get(url=cdn_url)
        self.assertIn('Access Denied', resp.content)

        # Verify wpt can fetch cdn content
        wpt_result = self.run_webpagetest(url=cdn_url)
        test_region = wpt_result.keys()[0]
        wpt_response_text = \
            wpt_result[
                test_region]['data']['runs']['1']['firstView']['requests'][
                0]['headers']['response'][0]
        self.assertIn(
            'HTTP/1.1 200', wpt_response_text)

    def test_ip_whitelist(self):
        test_domain = "{0}.{1}".format(
            base.random_string('test-whitelist-ip'),
            self.dns_config.test_domain)
        domains = [{'domain': test_domain}]
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        caching = [
            {"name": "default",
             "ttl": 3600,
             "rules": [{"name": "default", "request_url": "/*"}]}]

        test_system_ip = self.get_ip_address()
        restrictions = [
            {"name": "test_ip_whitelist",
             "type": "whitelist",
             "rules": [{"name": "whitelist",
                        "client_ip": test_system_ip,
                        "request_url": "/*"}]}]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        # Verify whitelisted IP can fetch cdn content
        cdn_url = 'http://' + test_domain
        resp = self.http_client.get(url=cdn_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.default_origin, resp.content)

        # Verify wpt cannot fetch cdn content
        wpt_result = self.run_webpagetest(url=cdn_url)
        test_region = wpt_result.keys()[0]
        wpt_response_text = \
            wpt_result[
                test_region]['data']['runs']['1']['firstView']['requests'][
                0]['headers']['response'][0]
        self.assertIn(
            'HTTP/1.1 403 Forbidden', wpt_response_text)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestIpRestrictions, self).tearDown()
