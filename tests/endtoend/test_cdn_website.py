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

import time

from tests.endtoend import base


class TestWebsiteCDN(base.TestBase):

    """Tests for CDN enabling a website."""

    def setUp(self):
        super(TestWebsiteCDN, self).setUp()

        sub_domain = base.random_string(prefix='TestCDN-')
        self.test_domain = sub_domain + '.' + self.dns_config.test_domain

        print('Domain Name', self.test_domain)

        self.origin = self.test_config.wordpress_origin
        self.cname_rec = []

    def test_enable_cdn(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
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

        rec = self.setup_cname(name=self.test_domain, cname=access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url)

        if self.test_config.webpagetest_enabled:
            self.run_webpagetest(url=cdn_enabled_url)

    def test_multiple_domains(self):

        # Create another domain in addition to the one created in setUp
        sub_domain2 = base.random_string(prefix='TestCDN-')
        self.test_domain2 = sub_domain2 + '.' + self.dns_config.test_domain

        print('Additional Domain Name', self.test_domain2)

        # Create a Poppy Service for the test website with two domains
        domain_list = [{"domain": self.test_domain},
                       {"domain": self.test_domain2}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
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

    def test_cache_rules(self):

        # Create a Poppy Service for the test website with cache rules
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]

        rule1 = self.cacherules_config.cache_rule1
        ttlrule1 = self.cacherules_config.ttl_rule1

        rule2 = self.cacherules_config.cache_rule2
        ttlrule2 = self.cacherules_config.ttl_rule2

        rule3 = self.cacherules_config.cache_rule3
        ttlrule3 = self.cacherules_config.ttl_rule3

        # Setup cache list using cache
        caching_list = [{"name": "images", "ttl": ttlrule1, "rules":
                        [{"name": "image_rule",
                          "request_url": rule1}]},
                        {"name": "images", "ttl": ttlrule2, "rules":
                        [{"name": "css_rule",
                          "request_url": rule2}]},
                        {"name": "images", "ttl": ttlrule3, "rules":
                        [{"name": "js_rule",
                          "request_url": rule3}]}]

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

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url)

        # Verify cdn hit on rule urls
        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule1, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule1,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule2, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule2,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule3, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule3,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(max(ttlrule1, ttlrule2, ttlrule3))
        # Verify that content in cache is stale/removed after the ttl expires
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule1,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule2,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule3,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

    def test_purge(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]

        rule1 = self.cacherules_config.cache_rule1
        ttlrule1 = self.cacherules_config.ttl_rule1

        caching_list = [{"name": "images", "ttl": ttlrule1, "rules":
                        [{"name": "image_rule", "request_url": rule1}]}]
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

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url,
                               cdn_url=cdn_enabled_url)

        # Purge object in rule 1 and ensure it gets a TCP_MISS
        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule1, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule1,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])
        self.poppy_client.purge_asset(location=self.service_location,
                                      asset_url=rule1)

        # Wait for purge to complete & verify that content is fetched from
        # origin for subsequent call.
        # @todo: Change the sleep to check the real status of purge. As is
        # there is no way a poppy user can get the purge status.
        time.sleep(self.purge_config.purge_wait_time)
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule1,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

        # Currently not supported
        # Purge all content and ensure rule 2 gets a TCP_MISS
        # self.poppy_client.purge_asset(location=self.service_location)
        # self.wait_for_CDN_status(cdn_url=cdn_enabled_url, status='TCP_MISS')
        # self.assertCDNMiss(cdn_url=cdn_enabled_url + rule2)

    def test_update_cache_rules(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.origin, "port": 80, "ssl": False}]

        rule1 = self.cacherules_config.cache_rule1
        ttlrule1 = self.cacherules_config.ttl_rule1

        caching_list = [{"name": "images", "ttl": ttlrule1, "rules":
                        [{"name": "image_rule", "request_url": rule1}]}]
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

        origin_url = 'http://' + self.origin
        cdn_enabled_url = 'http://' + self.test_domain

        self.assertSameContent(origin_url=origin_url, cdn_url=cdn_enabled_url)

        # Verify that content is cached after two requests
        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule1, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule1,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        # Verify that content in cache is stale/removed after the ttl expires
        time.sleep(ttlrule1 + 10)
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule1,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

        # Update cache rules
        new_ttl = 50
        test_data = [{"op": "replace",
                      "path": "/caching/0",
                      "value": {"name": "cache_name",
                                "ttl": new_ttl,
                                "rules": [{"name": "image_rule",
                                           "request_url": rule1}]}}]
        resp = self.poppy_client.patch_service(location=self.service_location,
                                               request_body=test_data)

        # Verify that content is cached after two requests
        self.get_from_cdn_enabled_url(cdn_url=cdn_enabled_url + rule1, count=2)
        self.assertCacheStatus(cdn_url=cdn_enabled_url + rule1,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(new_ttl)
        # Verify that content in cache is stale/removed after the ttl expires
        self.assertCacheStatus(
            cdn_url=cdn_enabled_url + rule1,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            print("deleting dns record: {0}".format(record))
            self.dns_client.delete_record(record)
        super(TestWebsiteCDN, self).tearDown()
