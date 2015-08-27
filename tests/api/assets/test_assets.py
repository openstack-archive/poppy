# -*- coding: utf8 -*-
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

import ddt
from nose.plugins import attrib

from tests.api import base


@ddt.ddt
class TestAssets(base.TestBase):

    """Tests for Assets."""

    def setUp(self):
        super(TestAssets, self).setUp()
        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor
        self.log_delivery = {"enabled": False}

        domain = self.generate_random_string(prefix='api-test-domain') + '.com'
        self.domain_list = [
            {
                "domain": domain,
                "protocol": "http"
            }
        ]

        origin = self.generate_random_string(prefix='api-test-origin') + '.com'
        self.origin_list = [
            {
                "origin": origin,
                "port": 80,
                "ssl": False,
                "rules": [
                    {
                        "name": "default",
                        "request_url": "/*"
                    }
                ]
            }
        ]

        self.caching_list = [
            {
                "name": "default",
                "ttl": 3600,
                "rules": [
                    {
                        "name": "default",
                        "request_url": "/*"
                    }
                ]
            },
            {
                "name": "home",
                "ttl": 1200,
                "rules": [
                    {
                        "name": "index",
                        "request_url": "/index.htm"
                    }
                ]
            }
        ]

        self.restrictions_list = [
            {"name": "website only",
             "type": "whitelist",
             "rules": [{"name": "mywebsite.com",
                        "referrer": "www.mywebsite.com",
                        "request_url": "/*"
                        }]}]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id,
            log_delivery=self.log_delivery)

        self.service_url = resp.headers["location"]

    @attrib.attr('smoke')
    @ddt.data('True', 'true', 'TRUE', 'TRue')
    def test_purge_assets_all(self, purge_all):

        url_param = {'all': purge_all}
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.headers["location"],
                         self.service_url)
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @ddt.data('mywebsite.com', 'images/maakri.jpg')
    def test_purge_assets_url_hard_invalidate(self, url):

        url_param = {
            'url': url,
            'hard': True
        }
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.headers["location"],
                         self.service_url)
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @ddt.data('mywebsite.com', 'images/maakri.jpg', 'images')
    def test_purge_assets_url_soft_invalidate(self, url):

        url_param = {
            'url': url,
            'hard': False
        }
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.headers["location"],
                         self.service_url)
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @ddt.data('mywebiste.com', 'images/maakri.jpg')
    def test_purge_assets_url_negative_invalidate_non_bool_hard(self, url):

        url_param = {
            'url': url,
            'hard': 'negative'
        }
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 400)

    @ddt.data('mywebiste.com', '/¢¢¢¢¢¢.jpg')
    def test_purge_assets_url_negative_invalidate_non_ascii_url(self, url):

        url_param = {
            'url': url,
            'hard': False
        }
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 400)

    @attrib.attr('smoke')
    def test_purge_assets_negative(self):

        url_param = {'url': 'myurl.com', 'all': True}
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 400)

    @attrib.attr('smoke')
    def test_purge_assets_no_url(self):

        url_param = {'url': 'myurl.com'}
        resp = self.client.purge_assets(location=self.service_url,
                                        param=url_param)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_service(location=self.service_location)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestAssets, self).tearDown()
