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
import uuid

from tests.api import base
from tests.api.utils.schema import services


@ddt.ddt
class TestGetServiceByDomain(base.TestBase):

    def setUp(self):
        super(TestGetServiceByDomain, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor

        domain1 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        domain2 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        domain3 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'

        self.domain_list = [
            {"domain": domain1, "protocol": "http"},
            {"domain": domain2, "protocol": "http"},
            {"domain": domain3, "protocol": "http"}
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
                u"access": u"whitelist",
                u"rules": [
                    {
                        u"name": domain1,
                        u"referrer": domain1,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    def test_get_service_by_domain(self):
        resp = self.operator_client.admin_get_service_by_domain_name(
            self.domain_list[0]['domain'])

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertSchema(body, services.get_service)

        for item in self.domain_list:
            if 'protocol' not in item:
                item['protocol'] = 'http'
        self.assertEqual(body['domains'], self.domain_list)

        for item in self.origin_list:
            if 'rules' not in item:
                item[u'rules'] = []
            if 'hostheadertype' not in item:
                item[u'hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item[u'hostheadervalue'] = item['origin']

        self.assertEqual(body['origins'], self.origin_list)
        self.assertEqual(body['caching'], self.caching_list)
        self.assertEqual(body['restrictions'], self.restrictions_list)
        self.assertEqual(body['flavor_id'], self.flavor_id)
        self.assertEqual(body['project_id'], self.user_project_id)

    def test_get_service_by_multiple_domains(self):
        api_resp = self.operator_client.admin_get_service_by_domain_name(
            self.domain_list[0]['domain'])
        self.assertEqual(api_resp.status_code, 200)

        api_resp1 = self.operator_client.admin_get_service_by_domain_name(
            self.domain_list[1]['domain'])
        self.assertEqual(api_resp1.status_code, 200)

        api_resp2 = self.operator_client.admin_get_service_by_domain_name(
            self.domain_list[2]['domain'])
        self.assertEqual(api_resp2.status_code, 200)

    def test_negative_get_by_non_existing_domain(self):
        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        domain_name = self.domain_list[0]['domain'] + str(uuid.uuid1()) + \
            ".com"
        resp = self.operator_client.admin_get_service_by_domain_name(
            domain_name)
        self.assertEqual(resp.status_code, 404)

    @ddt.data("http://www.non-existing-domain",
              "https://www.non-existing-domain",
              "http://www.קאַץ")
    def test_get_service_by_non_existing_bad_domain(self, domain):
        domain_name = domain + str(uuid.uuid1()) + ".com"
        resp = self.operator_client.admin_get_service_by_domain_name(
            domain_name)
        self.assertEqual(resp.status_code, 404)

    def test_get_service_negative_very_long_domain(self):
        domain = "www.too_long_name_too_long_name_too_long_name_too_long_" \
                 "name_too_long_name_too_long_name_too_long_name_too_long_" \
                 "name_too_long_name_too_long_name_too_long_name_too_long_" \
                 "name_too_long_name_too_long_name_too_long_name_too_long_" \
                 "name_too_long_name_too_long.com"

        resp = self.operator_client.admin_get_service_by_domain_name(domain)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestGetServiceByDomain, self).tearDown()


@ddt.ddt
class TestGetServiceBySharedDomain(base.TestBase):

    def setUp(self):
        super(TestGetServiceBySharedDomain, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

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
                ],
                u"access": "whitelist"
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    def test_get_service_by_domain(self):
        get_resp = self.client.get_service(self.service_url)
        resp_body = get_resp.json()
        domain = resp_body['domains'][0]['domain']
        resp = self.operator_client.admin_get_service_by_domain_name(domain)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertSchema(body, services.get_service)

        for item in self.origin_list:
            if 'rules' not in item:
                item[u'rules'] = []
            if 'hostheadertype' not in item:
                item[u'hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item[u'hostheadervalue'] = item['origin']

        self.assertEqual(body['origins'], self.origin_list)
        self.assertEqual(body['caching'], self.caching_list)
        self.assertEqual(body['restrictions'], self.restrictions_list)
        self.assertEqual(body['flavor_id'], self.flavor_id)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestGetServiceBySharedDomain, self).tearDown()


@ddt.ddt
class TestGetServiceBySANCertDomain(base.TestBase):

    def setUp(self):
        super(TestGetServiceBySANCertDomain, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
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
                ],
                u"access": "whitelist"
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.service_url = resp.headers["location"]

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    def test_get_service_by_domain(self):
        get_resp = self.client.get_service(self.service_url)
        resp_body = get_resp.json()
        domain = resp_body['domains'][0]['domain']
        resp = self.operator_client.admin_get_service_by_domain_name(domain)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertSchema(body, services.get_service)

        for item in self.origin_list:
            if 'rules' not in item:
                item[u'rules'] = []
            if 'hostheadertype' not in item:
                item[u'hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item[u'hostheadervalue'] = item['origin']

        self.assertEqual(body['origins'], self.origin_list)
        self.assertEqual(body['caching'], self.caching_list)
        self.assertEqual(body['restrictions'], self.restrictions_list)
        self.assertEqual(body['flavor_id'], self.flavor_id)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestGetServiceBySANCertDomain, self).tearDown()


@ddt.ddt
class TestGetServiceByCustomCertDomain(base.TestBase):

    def setUp(self):
        super(TestGetServiceByCustomCertDomain, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        self.service_name = self.generate_random_string(prefix='API-Test-')
        self.flavor_id = self.test_flavor

        domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
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
                ],
                u"access": "whitelist"
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    def test_get_service_by_domain(self):
        get_resp = self.client.get_service(self.service_url)
        resp_body = get_resp.json()
        domain = resp_body['domains'][0]['domain']
        resp = self.operator_client.admin_get_service_by_domain_name(domain)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertSchema(body, services.get_service)

        for item in self.origin_list:
            if 'rules' not in item:
                item[u'rules'] = []
            if 'hostheadertype' not in item:
                item[u'hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item[u'hostheadervalue'] = item['origin']

        self.assertEqual(body['origins'], self.origin_list)
        self.assertEqual(body['caching'], self.caching_list)
        self.assertEqual(body['restrictions'], self.restrictions_list)
        self.assertEqual(body['flavor_id'], self.flavor_id)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestGetServiceByCustomCertDomain, self).tearDown()
