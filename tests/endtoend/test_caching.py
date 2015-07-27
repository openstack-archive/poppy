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

import time

from tests.endtoend import base
from tests.endtoend.utils import config


class TestCaching(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestCaching, cls).setUpClass()

        cls.caching_config = config.CachingConfig()

        cls.default_origin = cls.caching_config.origin

        cls.cacheable_endpoint = cls.caching_config.endpoint
        cls.jpg_path = cls.caching_config.jpg_endpoint
        cls.txt_path = cls.caching_config.txt_endpoint
        cls.zip_path = cls.caching_config.zip_endpoint

        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.cacheable_endpoint)
        assert origin.status_code == 200

        jpg_origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.jpg_path)
        assert jpg_origin.status_code == 200

        txt_origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.txt_path)
        assert txt_origin.status_code == 200

        zip_origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.zip_path)
        assert zip_origin.status_code == 200

    def setUp(self):
        super(TestCaching, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-caching'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('E2E-CachingService')
        self.cname_rec = []

    def test_zero_caching(self):
        domains = [{'domain': self.test_domain}]
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
            "hostheadertype": "origin"
        }]
        caching = [
            {"name": "default",
             "ttl": 0,
             "rules": [{"name": "default", "request_url": "/*"}]}]
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain + self.cacheable_endpoint

        # Verify content is not cached
        self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=4)
        self.assertCacheStatus(cdn_url=cdn_url,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_cache_rules(self):

        # Create a Poppy Service for the test website with cache rules
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.default_origin,
                        "port": 80,
                        "ssl": False}]

        jpg_ttl = self.caching_config.jpg_ttl
        txt_ttl = self.caching_config.txt_ttl
        zip_ttl = self.caching_config.zip_ttl

        # Setup cache list using cache
        caching_list = [
            {"name": "jpg", "ttl": jpg_ttl,
             "rules": [{"name": "jpg_rule", "request_url": self.jpg_path}]},
            {"name": "txt", "ttl": txt_ttl,
             "rules": [{"name": "txt_rule", "request_url": self.txt_path}]},
            {"name": "zip", "ttl": zip_ttl,
             "rules": [{"name": "zip_rule", "request_url": self.zip_path}]}]

        self.service_name = base.random_string(prefix='testService-')

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

        origin_url = 'http://' + self.default_origin
        cdn_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url, cdn_url=cdn_url)

        # Verify cdn hit on rule urls
        cdn_jpg_url = cdn_url + self.jpg_path
        self.get_from_cdn_enabled_url(cdn_url=cdn_jpg_url, count=2)
        self.assertCacheStatus(cdn_url=cdn_jpg_url,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        cdn_txt_url = cdn_url + self.txt_path
        self.get_from_cdn_enabled_url(cdn_url=cdn_txt_url, count=2)
        self.assertCacheStatus(cdn_url=cdn_txt_url,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        cdn_zip_url = cdn_url + self.zip_path
        self.get_from_cdn_enabled_url(cdn_url=cdn_zip_url, count=2)
        self.assertCacheStatus(cdn_url=cdn_zip_url,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(max(jpg_ttl, zip_ttl, txt_ttl))
        # Verify that content in cache is stale/removed after the ttl expires
        self.assertCacheStatus(
            cdn_url=cdn_jpg_url,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])
        self.assertCacheStatus(
            cdn_url=cdn_txt_url,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])
        self.assertCacheStatus(
            cdn_url=cdn_zip_url,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestCaching, self).tearDown()
