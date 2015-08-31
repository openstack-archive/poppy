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


class TestReferrerRestriction(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestReferrerRestriction, cls).setUpClass()
        cls.test_domain = cls.dns_config.test_domain
        cls.referree_origin = cls.test_config.referree_origin
        cls.referrer_request_url = cls.test_config.referrer_request_url

    def setUp(self):
        super(TestReferrerRestriction, self).setUp()
        self.referree_domain = "{0}.{1}".format(
            base.random_string("referree"), self.test_domain)
        self.service_name = base.random_string("ReferrerRestrictionService")

        self.check_preconditions()

    def check_preconditions(self):
        # check preconditions. the referrer_request_url in the config needs to
        # give us a 200 response. the root domain should return a 200
        resp = self.http_client.get(
            "http://" + self.referree_origin + self.referrer_request_url)
        assert resp.status_code == 200
        resp = self.http_client.get("http://" + self.referree_origin)
        assert resp.status_code == 200

    def test_whitelist_referrer_restriction(self):
        domains = [{'domain': self.referree_domain}]
        origins = [{
            "origin": self.referree_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        restrictions = [{
            "name": "restriction",
            "rules": [{
                "name": "my site",
                "referrer": self.referree_domain,
            }]
        }]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)
        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        self.cname_rec = self.setup_cname(self.referree_domain, access_url[0])

        cdn_url = "http://" + self.referree_domain

        # fetching from a whitelisted referrer should work
        resp = self.http_client.get(cdn_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 200)

        # fetching from a restriction domain should not work
        resp = self.http_client.get(
            cdn_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 403)

        # fetching with no referrer should work
        # resp = self.http_client.get(cdn_url)
        # self.assertEqual(resp.status_code, 200)

    def test_blacklist_referrer_restriction(self):
        domains = [{'domain': self.referree_domain}]
        origins = [{
            "origin": self.referree_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        restrictions = [{
            "name": "restriction",
            "access": "blacklist",
            "rules": [{
                "name": "my site",
                "referrer": self.referree_domain,
            }]
        }]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)
        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        self.cname_rec = self.setup_cname(self.referree_domain, access_url[0])

        cdn_url = "http://" + self.referree_domain

        # fetching from a blacklisted referrer should be forbidden
        resp = self.http_client.get(cdn_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 403)

        # fetching from any other domain should work
        resp = self.http_client.get(
            cdn_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 200)

        # fetching with no referrer should return forbidden
        # resp = self.http_client.get(cdn_url)
        # self.assertEqual(resp.status_code, 403)

    def test_whitelist_referrer_restriction_with_request_url(self):

        domains = [{'domain': self.referree_domain}]
        origins = [{
            "origin": self.referree_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        restrictions = [{
            "name": "restriction",
            "rules": [{
                "name": "my site",
                "referrer": self.referree_domain,
                "request_url": self.referrer_request_url,
            }]
        }]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)
        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        self.cname_rec = self.setup_cname(self.referree_domain, access_url[0])

        cdn_url = "http://" + self.referree_domain
        restricted_url = cdn_url + self.referrer_request_url

        # fetching a restricted url with a whitelisted referrer should work
        resp = self.http_client.get(
            restricted_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 200)

        # fetching a restricted url with a bad referrer should fail
        resp = self.http_client.get(
            restricted_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 403)

        # fetching the restricted url with no referrer should work
        # resp = self.http_client.get(restricted_url)
        # self.assertEqual(resp.status_code, 200)

        # the root path is unrestricted. any or no referrer is allowed.
        resp = self.http_client.get(cdn_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 200)

        resp = self.http_client.get(
            cdn_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 200)

        resp = self.http_client.get(cdn_url)
        self.assertEqual(resp.status_code, 200)

    def test_blacklist_referrer_restriction_with_request_url(self):
        domains = [{'domain': self.referree_domain}]
        origins = [{
            "origin": self.referree_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
        }]
        restrictions = [{
            "name": "restriction",
            "access": "blacklist",
            "rules": [{
                "name": "my site",
                "referrer": self.referree_domain,
                "request_url": self.referrer_request_url,
            }]
        }]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            restrictions_list=restrictions,
            flavor_id=self.poppy_config.flavor)
        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        self.cname_rec = self.setup_cname(self.referree_domain, access_url[0])

        cdn_url = "http://" + self.referree_domain
        restricted_url = cdn_url + self.referrer_request_url

        # fetching a restricted url with a blacklisted referrer should be
        # forbidden
        resp = self.http_client.get(
            restricted_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 403)

        # fetching a restricted url with a bad referrer should be allowed
        resp = self.http_client.get(
            restricted_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 200)

        # fetching the restricted url with no referrer should work
        # resp = self.http_client.get(restricted_url)
        # self.assertEqual(resp.status_code, 200)

        # the root path is unrestricted. any or no referrer is allowed.
        resp = self.http_client.get(cdn_url, headers={'Referer': cdn_url})
        self.assertEqual(resp.status_code, 200)

        resp = self.http_client.get(
            cdn_url, headers={'Referer': "http://badsite.com"})
        self.assertEqual(resp.status_code, 200)

        resp = self.http_client.get(cdn_url)
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        # if the test fails early the service_location and cname_rec attributes
        # may not exist. check for these attrs to avoid errors during teardown.
        if hasattr(self, 'service_location'):
            self.poppy_client.delete_service(location=self.service_location)
        if hasattr(self, 'cname_rec'):
            for record in self.cname_rec:
                self.dns_client.delete_record(record)
        super(TestReferrerRestriction, self).tearDown()
