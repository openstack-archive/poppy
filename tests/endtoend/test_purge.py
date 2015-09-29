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


class TestPurge(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestPurge, cls).setUpClass()

        cls.default_origin = cls.test_config.default_origin

        cls.purge_config = config.PurgeConfig()
        cls.purge_path = cls.purge_config.purge_path

        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.purge_path)
        assert origin.status_code == 200

    def setUp(self):
        super(TestPurge, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-purge'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('E2E-PurgeService')
        self.cname_rec = []

    def test_purge(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.default_origin,
                        "port": 80,
                        "ssl": False}]

        ttl = self.purge_config.cache_ttl

        caching_list = [{
            "name": "test_purge", "ttl": ttl,
            "rules": [{
                "name": "test_purge_rule", "request_url": self.purge_path}
            ]}]

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

        cdn_jpg_url = cdn_url + self.purge_path
        # Purge object in rule 1 and ensure it gets a TCP_MISS
        edge_server = self.get_from_cdn_enabled_url(
            cdn_url=cdn_jpg_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_jpg_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])
        url_param = {
            'url': self.purge_path,
            'hard': False
        }
        self.poppy_client.purge_assets(location=self.service_location,
                                       param=url_param)

        # Wait for purge to complete & verify that content is fetched from
        # origin for subsequent call.
        # @todo: Change the sleep to check the real status of purge. As is
        # there is no way a poppy user can get the purge status.
        time.sleep(self.purge_config.purge_wait_time)
        self.assertCacheStatus(
            cdn_url=cdn_jpg_url,
            status_list=['TCP_REFRESH_HIT', 'TCP_REFRESH_MISS', 'TCP_MISS'])

        # Currently not supported
        # Purge all content and ensure rule 2 gets a TCP_MISS
        # self.poppy_client.purge_asset(location=self.service_location)
        # self.wait_for_CDN_status(cdn_url=cdn_enabled_url, status='TCP_MISS')
        # self.assertCDNMiss(cdn_url=cdn_enabled_url + rule2)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            print("deleting dns record: {0}".format(record))
            self.dns_client.delete_record(record)
        super(TestPurge, self).tearDown()


class TestCacheInvalidation(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestCacheInvalidation, cls).setUpClass()

        cls.default_origin = cls.test_config.default_origin

        cls.purge_config = config.PurgeConfig()
        cls.purge_path = cls.purge_config.purge_path

        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.purge_path)
        assert origin.status_code == 200

    def setUp(self):
        super(TestCacheInvalidation, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-invalidate-cache'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('E2E-InvalidateCache')
        self.cname_rec = []

    def test_invalidate_cache(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.test_domain}]
        origin_list = [{"origin": self.default_origin,
                        "port": 80,
                        "ssl": False}]

        ttl = self.purge_config.cache_ttl

        caching_list = [{
            "name": "test_invalidate_cache", "ttl": ttl,
            "rules": [{
                "name": "invalidate_cache", "request_url": self.purge_path}
            ]}]

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

        cdn_jpg_url = cdn_url + self.purge_path
        edge_server = self.get_from_cdn_enabled_url(
            cdn_url=cdn_jpg_url, count=1)
        self.assertCacheStatus(
            cdn_url=cdn_jpg_url, edge_server=edge_server,
            status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        # Purge object in cdn_jpg_url and ensure it gets a TCP_MISS
        url_param = {
            'url': self.purge_path,
            'hard': False
        }
        self.poppy_client.purge_assets(location=self.service_location,
                                       param=url_param)

        # Wait for purge to complete & verify that content is fetched from
        # origin for subsequent call.
        # @todo: Change the sleep to check the real status of purge. As is
        # there is no way a poppy user can get the purge status.
        # time.sleep(self.purge_config.purge_wait_time)
        self.poppy_client.wait_for_service_status(
            location=self.service_location, status='DEPLOYED')
        # Sleep of 60 sec is in accordance with Akamai's SLA for cache
        # invalidation.
        time.sleep(60)
        self.assertCacheStatus(
            cdn_url=cdn_jpg_url, edge_server=edge_server,
            status_list=['TCP_REFRESH_MISS'])

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            print("deleting dns record: {0}".format(record))
            self.dns_client.delete_record(record)
        super(TestCacheInvalidation, self).tearDown()
