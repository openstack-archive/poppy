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

import ddt

from tests.api import base


@ddt.ddt
class TestHttpService(base.TestBase):

    def setUp(self):
        super(TestHttpService, self).setUp()
        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='api-test-domain') + u'.com'
        self.domain_list = [
            {"domain": domain, "protocol": "http"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 80,
                u"ssl": False,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": domain,
                        u"referrer": domain,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.client.create_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]
        resp = self.client.wait_for_service_status(
            location=self.service_url, status='deployed')
        self.before_patch_body = resp.json()
        self.before_patch_state = resp.json()['status']

    @ddt.data('enabled', 'disabled')
    def test_update_state(self, new_state):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state=new_state)
        self.assertEqual(resp.status_code, 202)

        if new_state == 'enabled':
            expected_new_state = self.before_patch_state
        else:
            expected_new_state = 'disabled'

        self.client.wait_for_service_status(
            location=self.service_url, status=expected_new_state)

        resp = self.client.get_service(location=self.service_url)
        after_patch_body = resp.json()
        after_patch_state = after_patch_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_patch_state, expected_new_state)

        del self.before_patch_body['status']
        del after_patch_body['status']

        self.assertEqual(
            sorted(after_patch_body), sorted(self.before_patch_body))

    def test_update_state_disabled_to_enabled(self):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='disabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='disabled')

        resp = self.client.get_service(location=self.service_url)
        updated_state = resp.json()['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'disabled')

        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='enabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='deployed')

        resp = self.client.get_service(location=self.service_url)
        updated_body = resp.json()
        updated_state = updated_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'deployed')

        self.assertEqual(updated_body, self.before_patch_body)

    @ddt.data('MY_CRAZY_STATE')
    def test_update_state_negative(self, new_state):
        resp = self.client.get_service(location=self.service_url)
        before_patch_state = resp.json()['status']

        resp = self.client.update_service_state(location=self.service_url,
                                                new_state=new_state)
        self.assertEqual(resp.status_code, 400)

        self.client.wait_for_service_status(
            location=self.service_url, status='deployed')

        resp = self.client.get_service(location=self.service_url)
        after_patch_state = resp.json()['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(before_patch_state, after_patch_state)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestHttpService, self).tearDown()


@ddt.ddt
class TestSharedCertService(base.TestBase):

    def setUp(self):
        super(TestSharedCertService, self).setUp()
        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='api-test-domain')
        self.domain_list = [
            {"domain": domain, "protocol": "https", "certificate": "shared"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 443,
                u"ssl": True,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": domain,
                        u"referrer": "domain.com",
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.client.create_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]
        resp = self.client.wait_for_service_status(
            location=self.service_url, status='deployed')
        self.before_patch_body = resp.json()
        self.before_patch_state = resp.json()['status']

    @ddt.data('enabled', 'disabled')
    def test_update_state(self, new_state):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state=new_state)
        self.assertEqual(resp.status_code, 202)

        if new_state == 'enabled':
            expected_new_state = self.before_patch_state
        else:
            expected_new_state = 'disabled'

        self.client.wait_for_service_status(
            location=self.service_url, status=expected_new_state)

        resp = self.client.get_service(location=self.service_url)
        after_patch_body = resp.json()
        after_patch_state = after_patch_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_patch_state, expected_new_state)

        del self.before_patch_body['status']
        del after_patch_body['status']

        self.assertEqual(
            sorted(after_patch_body), sorted(self.before_patch_body))

    def test_update_state_disabled_to_enabled(self):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='disabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='disabled')

        resp = self.client.get_service(location=self.service_url)
        updated_state = resp.json()['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'disabled')

        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='enabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='deployed')

        resp = self.client.get_service(location=self.service_url)
        updated_body = resp.json()
        updated_state = updated_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'deployed')

        self.assertEqual(updated_body, self.before_patch_body)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestSharedCertService, self).tearDown()


@ddt.ddt
class TestSanCertService(base.TestBase):

    def setUp(self):
        super(TestSanCertService, self).setUp()
        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='api-test-domain') + '.com'
        self.domain_list = [
            {"domain": domain, "protocol": "https", "certificate": "san"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 443,
                u"ssl": True,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": domain,
                        u"referrer": domain,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.client.create_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]
        resp = self.client.wait_for_service_status(
            location=self.service_url, status='deployed')
        self.before_patch_body = resp.json()
        self.before_patch_state = resp.json()['status']

    @ddt.data('enabled', 'disabled')
    def test_update_state(self, new_state):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state=new_state)
        self.assertEqual(resp.status_code, 202)

        if new_state == 'enabled':
            expected_new_state = self.before_patch_state
        else:
            expected_new_state = 'disabled'

        self.client.wait_for_service_status(
            location=self.service_url, status=expected_new_state)

        resp = self.client.get_service(location=self.service_url)
        after_patch_body = resp.json()
        after_patch_state = after_patch_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_patch_state, expected_new_state)

        del self.before_patch_body['status']
        del after_patch_body['status']

        self.assertEqual(
            sorted(after_patch_body), sorted(self.before_patch_body))

    def test_update_state_disabled_to_enabled(self):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='disabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='disabled')

        resp = self.client.get_service(location=self.service_url)
        updated_state = resp.json()['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'disabled')

        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='enabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='deployed')

        resp = self.client.get_service(location=self.service_url)
        updated_body = resp.json()
        updated_state = updated_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'deployed')

        self.assertEqual(updated_body, self.before_patch_body)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestSanCertService, self).tearDown()


@ddt.ddt
class TestCustomCertService(base.TestBase):

    def setUp(self):
        super(TestCustomCertService, self).setUp()
        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='api-test-domain') + '.com'
        self.domain_list = [
            {"domain": domain, "protocol": "https", "certificate": "custom"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 443,
                u"ssl": True,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": domain,
                        u"referrer": domain,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.client.create_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]
        resp = self.client.wait_for_service_status(
            location=self.service_url, status='deployed')
        self.before_patch_body = resp.json()
        self.before_patch_state = resp.json()['status']

    @ddt.data('enabled', 'disabled')
    def test_update_state(self, new_state):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state=new_state)
        self.assertEqual(resp.status_code, 202)

        if new_state == 'enabled':
            expected_new_state = self.before_patch_state
        else:
            expected_new_state = 'disabled'

        self.client.wait_for_service_status(
            location=self.service_url, status=expected_new_state)

        resp = self.client.get_service(location=self.service_url)
        after_patch_body = resp.json()
        after_patch_state = after_patch_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_patch_state, expected_new_state)

        del self.before_patch_body['status']
        del after_patch_body['status']

        self.assertEqual(
            sorted(after_patch_body), sorted(self.before_patch_body))

    def test_update_state_disabled_to_enabled(self):
        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='disabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='disabled')

        resp = self.client.get_service(location=self.service_url)
        updated_state = resp.json()['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'disabled')

        resp = self.client.update_service_state(location=self.service_url,
                                                new_state='enabled')
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url, status='deployed')

        resp = self.client.get_service(location=self.service_url)
        updated_body = resp.json()
        updated_state = updated_body['status']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(updated_state, 'deployed')

        self.assertEqual(updated_body, self.before_patch_body)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestCustomCertService, self).tearDown()
