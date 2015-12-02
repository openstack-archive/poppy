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
import jsonpatch

from tests.api import base
from tests.api.utils.schema import services


@ddt.ddt
class TestCreateSSLService(base.TestBase):

    """Tests for Create Service."""

    def setUp(self):
        super(TestCreateSSLService, self).setUp()

        self.service_url = ''
        self.service_name = self.generate_random_string(
            prefix='api-test-service')
        self.flavor_id = self.test_flavor

    @ddt.file_data('data_create_service_ssl_domain.json')
    def test_create_service_ssl_domain_positive(self, test_data):

        domain_list = test_data['domain_list']
        for item in domain_list:
            if item['certificate'] == 'shared':
                item['domain'] = self.generate_random_string(
                    prefix='shared-ssl')
            else:
                item['domain'] = self.generate_random_string(
                    prefix='www.ssl-domain') + '.com'

        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        log_delivery = test_data.get('log_delivery')
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id,
                                          log_delivery=log_delivery)
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        resp = self.client.get_service(location=self.service_url)
        self.assertEqual(resp.status_code, 200)

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        resp = self.client.get_service(location=self.service_url)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        status = body['status']
        self.assertEqual(status, 'deployed')

        self.assertSchema(body, services.get_service)

        for item in domain_list:
            if 'protocol' not in item:
                item['protocol'] = 'http'
            elif item['protocol'] == 'https':
                matched_domain_in_body = next(
                    b_item for b_item in body['domains']
                    if (b_item['domain'] == item['domain']) or
                       (b_item['certificate'] == 'shared' and
                        item['domain'] == b_item['domain'].split('.')[0]))
                if item['certificate'] == 'shared':
                    item['certificate_status'] = 'deployed'
                    item['domain'] = matched_domain_in_body['domain']
                elif item['certificate'] == 'san':
                    item['certificate_status'] = 'create_in_progress'
                else:
                    item['certificate_status'] = (
                        matched_domain_in_body['certificate_status'])
        self.assertEqual(body['domains'], domain_list)

        for item in origin_list:
            if 'rules' not in item:
                item[u'rules'] = []
            if 'hostheadertype' not in item:
                item[u'hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item[u'hostheadervalue'] = item['origin']
        self.assertEqual(body['origins'], origin_list)
        if log_delivery:
            self.assertEqual(body['log_delivery'], log_delivery)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestCreateSSLService, self).tearDown()


@ddt.ddt
class TestPatchSSLService(base.TestBase):

    """Tests for Patch SSL Service."""

    def setUp(self):
        super(TestPatchSSLService, self).setUp()

        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor
        self.log_delivery = {"enabled": False}

        domain = self.generate_random_string(prefix='api-test-domain')
        self.domain_list = [
            {
                "domain": domain,
                "protocol": "https",
                "certificate": "shared"
            }
        ]

        origin = self.generate_random_string(prefix='api-test-origin') + '.com'
        self.origin_list = [
            {
                "origin": origin,
                "port": 443,
                "ssl": True,
                "rules": [
                    {
                        "name": "default",
                        "request_url": "/*"
                    }],
                "hostheadertype": "custom",
                "hostheadervalue": "www.customweb.com"
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
             # add whitelist to make restriction type explicit
             "access": "whitelist",
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

        self.original_service_details = {
            "name": self.service_name,
            "domains": self.domain_list,
            "origins": self.origin_list,
            "caching": self.caching_list,
            "restrictions": self.restrictions_list,
            "flavor_id": self.flavor_id,
            "log_delivery": self.log_delivery}

    def _replace_domain(self, domain):
        if ('protocol' in domain):
            if domain['protocol'] == 'https':
                if (domain['certificate'] == u'shared'):
                    return self.generate_random_string(prefix='api-test-ssl')

        return self.generate_random_string(prefix='www.api-test-ssl') + '.com'

    @ddt.file_data('data_patch_service_ssl_domain.json')
    def test_patch_ssl_domain(self, test_data):

        for item in test_data:
            if ('domain' in item['path']) and ('value' in item):
                if isinstance(item['value'], (list)):
                    item['value'][0]['domain'] = self._replace_domain(
                        domain=item['value'][0])
                else:
                    item['value']['domain'] = self._replace_domain(
                        domain=item['value'])

        patch = jsonpatch.JsonPatch(test_data)
        expected_service_details = patch.apply(self.original_service_details)

        # Default restriction to whitelist
        expected_restrictions = expected_service_details['restrictions']
        for restriction in expected_restrictions:
            if 'access' not in restriction:
                restriction['access'] = 'whitelist'

        resp = self.client.patch_service(location=self.service_url,
                                         request_body=test_data)
        self.assertEqual(resp.status_code, 202)

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        resp = self.client.get_service(location=self.service_url)
        body = resp.json()
        self.assertEqual(body['status'], 'deployed')

        self.assert_patch_service_details(body, expected_service_details)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestPatchSSLService, self).tearDown()
