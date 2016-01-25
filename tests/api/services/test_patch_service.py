# coding= utf-8

# Copyright (c) 2014 Rackspace, Inc.
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
import uuid

import ddt
import jsonpatch

from tests.api import base


@ddt.ddt
class TestServicePatch(base.TestBase):

    """Tests for PATCH Services."""

    def setUp(self):
        super(TestServicePatch, self).setUp()
        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor
        self.log_delivery = {"enabled": False}

        domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
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

    @ddt.file_data('data_patch_service.json')
    def test_patch_service(self, test_data):
        for item in test_data:
            if 'skip_test' in item:
                self.skipTest('Not Implemented - bug# 1433807')

            if ('domain' in item['path']) and ('value' in item):
                if isinstance(item['value'], (list)):
                    item['value'][0]['domain'] = self._replace_domain(
                        domain=item['value'][0])
                else:
                    item['value']['domain'] = self._replace_domain(
                        domain=item['value'])

        patch = jsonpatch.JsonPatch(test_data)
        expected_service_details = patch.apply(self.original_service_details)

        # Default restriciton to whitelist
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

        expected_origin = expected_service_details['origins']
        for field in expected_origin:
            if 'hostheadertype' not in field:
                field['hostheadertype'] = 'domain'
            elif field['hostheadertype'] == 'origin':
                field['hostheadervalue'] = field['origin']

        self.assert_patch_service_details(body, expected_service_details)

    def test_repatch_add_domain_service_after_domain_deletion(self):

        additional_domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'

        def _patch_add_domain(domain):

            patch_add_domain = [
                {
                    "op": "add",
                    "path": "/domains/-",
                    "value": {
                        "domain": domain, "protocol": "http"
                    }
                }
            ]

            resp = self.client.patch_service(location=self.service_url,
                                             request_body=patch_add_domain)
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

        # NOTE(TheSriram): Patch and add a domain.
        _patch_add_domain(domain=additional_domain)

        # NOTE(TheSriram): Delete the domain, that was just added.
        delete_domain = [
            {
                "op": "remove",
                "path": "/domains/1"
            }
        ]

        resp = self.client.patch_service(location=self.service_url,
                                         request_body=delete_domain)
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

        # NOTE(TheSriram): Re-add the deleted domain, this should go through
        # as the corresponding entry for that domain, should have been removed
        # from the storage layer.

        _patch_add_domain(domain=additional_domain)

    def test_repatch_add_same_domain_with_different_protocol(self):

        additional_domain = self.domain_list[0]['domain']

        patch_add_domain = [
            {
                "op": "add",
                "path": "/domains/-",
                "value": {
                    "domain": additional_domain,
                    "protocol": "https",
                    "certificate": "san"
                }
            }
        ]

        resp = self.client.patch_service(location=self.service_url,
                                         request_body=patch_add_domain)
        self.assertEqual(resp.status_code, 400)

    @ddt.file_data('data_patch_service_negative.json')
    def test_patch_service_HTTP_400(self, test_data):

        resp = self.client.patch_service(location=self.service_url,
                                         request_body=test_data)
        self.assertEqual(resp.status_code, 400)

        # nothing should have changed.
        resp = self.client.get_service(location=self.service_url)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(body['status'], 'deployed')

        expected_origin = self.original_service_details['origins']
        for field in expected_origin:
            if 'hostheadertype' not in field:
                field['hostheadertype'] = 'domain'
            elif field['hostheadertype'] == 'origin':
                field['hostheadervalue'] = field['origin']
        self.assert_patch_service_details(body, self.original_service_details)

    def test_patch_service_claim_relinquish_domain(self):
        newdomain = "www." + str(uuid.uuid4()) + ".com"
        add_domain = (
            [{
                "op": "add",
                "path": "/domains/-",
                "value": {"domain": newdomain, "protocol": "http"}
            }])
        remove_domain = (
            [{
                "op": "remove",
                "path": "/domains/1"
            }])

        # add new domain
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=add_domain)
        self.assertEqual(resp.status_code, 202)

        # wait for the domain to be added
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        # make sure the new domain is added
        resp = self.client.get_service(location=self.service_url)
        body = resp.json()
        self.assertEqual(body['status'], 'deployed')
        self.assertEqual(body['domains'][-1]['domain'], newdomain)

        # remove the new domain
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=remove_domain)
        self.assertEqual(resp.status_code, 202)

        # wait for the domain to be removed
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)
        # make sure the new domain is removed
        resp = self.client.get_service(location=self.service_url)
        body = resp.json()
        self.assertEqual(body['status'], 'deployed')
        for domain in body['domains']:
            self.assertNotEqual(domain['domain'], newdomain)

        # add new domain, again
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=add_domain)
        self.assertEqual(resp.status_code, 202)

        # wait for the domain to be added
        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        # make sure the new domain is added
        resp = self.client.get_service(location=self.service_url)
        body = resp.json()
        self.assertEqual(body['status'], 'deployed')
        self.assertEqual(body['domains'][-1]['domain'], newdomain)

    def test_patch_service_add_duplicate_domain(self):

        # create second service
        service_name = str(uuid.uuid1())
        duplicate_domain = 'www.' + str(uuid.uuid1()) + '.com'
        domain_list = [{"domain": duplicate_domain, "protocol": "http"}]

        origin = str(uuid.uuid1()) + '.com'
        origin_list = [{"origin": origin,
                        "port": 80, "ssl": False, "rules": []}]

        resp = self.client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            flavor_id=self.flavor_id)

        service_url = resp.headers["location"]

        # wait until the service is deployed
        self.client.wait_for_service_status(
            location=service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        resp = self.client.get_service(location=service_url)
        body = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body['status'], 'deployed')

        # wait to make sure cassandra is eventually consistent
        time.sleep(self.test_config.cassandra_consistency_wait_time)

        # patch original service with the duplicate domain
        add_duplicate_domain = (
            [{
                "op": "add",
                "path": "/domains/-",
                "value": {"domain": duplicate_domain, "protocol": "http"}
            }])

        # add the duplicate domain
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=add_duplicate_domain)
        self.assertEqual(resp.status_code, 400)

        self.client.delete_service(location=service_url)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestServicePatch, self).tearDown()


@ddt.ddt
class TestServicePatchWithLogDelivery(base.TestBase):

    """Tests for PATCH Services."""

    def setUp(self):
        super(TestServicePatchWithLogDelivery, self).setUp()
        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor
        self.log_delivery = {"enabled": True}

        domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
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

    @ddt.file_data('data_patch_service.json')
    def test_patch_service(self, test_data):

        for item in test_data:
            if 'skip_test' in item:
                self.skipTest('Not Implemented - bug# 1433807')

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

        expected_origin = expected_service_details['origins']
        for item in expected_origin:
            if 'hostheadertype' not in item:
                item['hostheadertype'] = 'domain'

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

        expected_origin = expected_service_details['origins']
        for item in expected_origin:
            if 'hostheadertype' not in item:
                item['hostheadertype'] = 'domain'
            elif item['hostheadertype'] == 'origin':
                item['hostheadervalue'] = item['origin']

        self.assert_patch_service_details(body, expected_service_details)

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestServicePatchWithLogDelivery, self).tearDown()
