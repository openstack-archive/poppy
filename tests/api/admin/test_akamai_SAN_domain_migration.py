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
import random

from tests.api import base


@ddt.ddt
class TestSanCertService(base.TestBase):

    def setUp(self):
        super(TestSanCertService, self).setUp()
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

    def test_migrate(self):

        new_certs = self.akamai_config.san_certs
        new_certs_list = new_certs.split(',')
        index = random.randint(0, len(new_certs_list) - 1)
        new_cert = new_certs_list[index]

        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = get_resp_body['domains'][0]['domain']
        resp = self.operator_client.admin_migrate_domain(
            project_id=self.user_project_id, service_id=get_resp_body['id'],
            domain=domain, new_cert=new_cert)

        self.assertEqual(resp.status_code, 202)

        new_resp = self.client.get_service(location=self.service_url)
        new_resp_body = new_resp.json()

        for link in new_resp_body['links']:
            if link['rel'] == 'access_url':
                access_url = link['href']

        dns_suffix = str(self.dns_config.dns_url_suffix)
        akamai_access_url_suffix = str(self.akamai_config.access_url_suffix)
        data = self.dns_client.verify_domain_migration(access_url=access_url,
                                                       suffix=dns_suffix)
        # Akamai specific suffix
        if not new_cert.endswith(akamai_access_url_suffix):
            new_cert = new_cert + "." + akamai_access_url_suffix

        self.assertEqual(data, new_cert)

    def test_migrate_negative_invalid_projectid(self):

        new_certs = self.akamai_config.san_certs
        new_certs_list = new_certs.split(',')
        index = random.randint(0, len(new_certs_list) - 1)
        new_cert = new_certs_list[index]

        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = get_resp_body['domains'][0]['domain']
        project_id = self.generate_random_string(prefix=self.user_project_id)
        resp = self.operator_client.admin_migrate_domain(
            project_id=project_id, service_id=get_resp_body['id'],
            domain=domain, new_cert=new_cert)

        self.assertEqual(resp.status_code, 404)

    def test_migrate_negative_invalid_serviceid(self):

        new_certs = self.akamai_config.san_certs
        new_certs_list = new_certs.split(',')
        index = random.randint(0, len(new_certs_list) - 1)
        new_cert = new_certs_list[index]

        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = get_resp_body['domains'][0]['domain']
        service_id = self.generate_random_string(prefix=get_resp_body['id'])
        resp = self.operator_client.admin_migrate_domain(
            project_id=self.user_project_id, service_id=service_id,
            domain=domain, new_cert=new_cert)

        self.assertEqual(resp.status_code, 404)

    def test_migrate_negative_invalid_domain(self):

        new_certs = self.akamai_config.san_certs
        new_certs_list = new_certs.split(',')
        index = random.randint(0, len(new_certs_list) - 1)
        new_cert = new_certs_list[index]

        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = "1234"
        service_id = self.generate_random_string(prefix=get_resp_body['id'])
        resp = self.operator_client.admin_migrate_domain(
            project_id=self.user_project_id, service_id=service_id,
            domain=domain, new_cert=new_cert)

        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestSanCertService, self).tearDown()


@ddt.ddt
class TestSanCertServiceWithLogDelivery(base.TestBase):

    def setUp(self):
        super(TestSanCertServiceWithLogDelivery, self).setUp()

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
                ]
            }
        ]

        self.log_delivery = {"enabled": True}

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id,
            log_delivery=self.log_delivery)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    def test_migrate(self):
        new_certs = self.akamai_config.san_certs
        new_certs_list = new_certs.split(',')
        index = random.randint(0, len(new_certs_list) - 1)
        new_cert = new_certs_list[index]
        get_resp = self.client.get_service(location=self.service_url)
        get_resp_body = get_resp.json()
        domain = get_resp_body['domains'][0]['domain']

        resp = self.operator_client.admin_migrate_domain(
            project_id=self.user_project_id, service_id=get_resp_body['id'],
            domain=domain, new_cert=new_cert)
        self.assertEqual(resp.status_code, 202)

        new_resp = self.client.get_service(location=self.service_url)
        new_resp_body = new_resp.json()

        for link in new_resp_body['links']:
            if link['rel'] == 'access_url':
                access_url = link['href']

        dns_suffix = str(self.dns_config.dns_url_suffix)
        akamai_access_url_suffix = str(self.akamai_config.access_url_suffix)
        data = self.dns_client.verify_domain_migration(access_url=access_url,
                                                       suffix=dns_suffix)
        # Akamai specific suffix
        if not new_cert.endswith(akamai_access_url_suffix):
            new_cert = new_cert + "." + akamai_access_url_suffix

        self.assertEqual(str(data), str(new_cert))

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestSanCertServiceWithLogDelivery, self).tearDown()
