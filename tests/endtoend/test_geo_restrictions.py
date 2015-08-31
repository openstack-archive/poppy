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
from tests.endtoend.utils import config


class TestGeoRestrictions(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestGeoRestrictions, cls).setUpClass()

        cls.test_config = config.TestConfig()
        cls.check_preconditions()

        cls.geo_restrictions_config = config.GeoRestrictionsConfig()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get("http://" + cls.default_origin)

        assert origin.status_code == 200

    def setUp(self):
        super(TestGeoRestrictions, self).setUp()
        self.service_name = base.random_string('E2E-Geo-Restriction')
        self.cname_rec = []

        self.service_location = ''

    def test_geo_whitelist(self):
        test_domain = "{0}.{1}".format(
            base.random_string('test-whitelist-geo'),
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

        restrictions = [
            {"name": "test_geo_whitelist",
             "access": "whitelist",
             "rules": [{"name": "whitelist",
                        "geography": self.geo_restrictions_config.test_geo,
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

        # Verify that not whitelisted geo cannot fetch cdn content
        cdn_url = 'http://' + test_domain
        resp = self.http_client.get(url=cdn_url)
        self.assertEqual(resp.status_code, 403)
        self.assertIn('Access Denied', resp.content)

        # Verify whitelisted geo can fetch cdn content
        wpt_result = self.run_webpagetest(url=cdn_url)
        test_region = wpt_result.keys()[0]
        wpt_response_text = \
            wpt_result[
                test_region]['data']['runs']['1']['firstView']['requests'][
                0]['headers']['response'][0]
        self.assertIn(
            'HTTP/1.1 200', wpt_response_text)

    def test_geo_blacklist(self):
        test_domain = "{0}.{1}".format(
            base.random_string('test-blacklist-geo'),
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

        restrictions = [
            {"name": "test_geo_blacklist",
             "access": "blacklist",
             "rules": [{"name": "blacklist",
                        "geography": self.geo_restrictions_config.test_geo,
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

        # Verify not blacklisted geo can fetch cdn content
        cdn_url = 'http://' + test_domain
        resp = self.http_client.get(url=cdn_url)
        self.assertEqual(resp.status_code, 200)

        # Verify blacklisted geo cannot fetch cdn content
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
        super(TestGeoRestrictions, self).tearDown()
