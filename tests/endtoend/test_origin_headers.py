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


class TestOriginHeaders(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestOriginHeaders, cls).setUpClass()

        cls.origin_header_config = config.OriginHeaderConfig()

        cls.expires_path = cls.origin_header_config.expires_path
        cls.cache_control_path = \
            cls.origin_header_config.cache_control_path
        cls.expires_and_cache_control_path = \
            cls.origin_header_config.expires_and_cache_control_path
        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        expires_path = cls.http_client.get(
            "http://" + cls.default_origin + cls.expires_path)
        assert expires_path.status_code == 200

        cache_control_path = cls.http_client.get(
            "http://" + cls.default_origin + cls.cache_control_path)
        assert cache_control_path.status_code == 200

        expires_and_cache_control_path = cls.http_client.get(
            "http://" + cls.default_origin +
            cls.expires_and_cache_control_path)
        assert expires_and_cache_control_path.status_code == 200

    def _delete_caching_rules(self):
        """Deletes any caching rule associated with the service."""
        patch_body = [{"op": "remove", "path": "/caching/0"}]
        self.poppy_client.patch_service(location=self.service_location,
                                        request_body=patch_body)
        self.poppy_client.wait_for_service_status(
            location=self.service_location, status='DEPLOYED')

    def setUp(self):
        super(TestOriginHeaders, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-origin-headers'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('OriginHeaderService')
        self.cname_rec = []

    def test_expires_header_no_caching_ttl(self):
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
        caching = []
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        self._delete_caching_rules()

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain + self.expires_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.expires_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_expires_header_with_caching_ttl(self):
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
             "ttl": self.origin_header_config.service_ttl,
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

        cdn_url = 'http://' + self.test_domain + self.expires_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.expires_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.service_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_cache_control_header_no_caching_ttl(self):
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
        caching = []
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        self._delete_caching_rules()
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain + self.cache_control_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.cache_control_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_cache_control_header_with_caching_ttl(self):
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
             "ttl": self.origin_header_config.service_ttl,
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

        cdn_url = 'http://' + self.test_domain + self.expires_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.cache_control_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.service_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_expires_and_cache_control_header_no_caching_ttl(self):
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
        caching = []
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        self._delete_caching_rules()
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = \
            'http://' + self.test_domain + self.expires_and_cache_control_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=4)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.cache_control_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def test_expires_and_cache_control_header_with_caching_ttl(self):
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
             "ttl": self.origin_header_config.service_ttl,
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

        cdn_url = \
            'http://' + self.test_domain + self.expires_and_cache_control_path
        edge_server = self.get_from_cdn_enabled_url(cdn_url=cdn_url, count=1)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.cache_control_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_HIT', 'TCP_MEM_HIT'])

        time.sleep(self.origin_header_config.service_ttl + 2)
        self.assertCacheStatus(cdn_url=cdn_url, edge_server=edge_server,
                               status_list=['TCP_MISS', 'TCP_REFRESH_MISS'])

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestOriginHeaders, self).tearDown()
