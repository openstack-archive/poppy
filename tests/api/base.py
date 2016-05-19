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

import random
import string
import uuid

from cafe.drivers.unittest import fixtures
import jsonschema

from tests.api.utils import client
from tests.api.utils import config


class TestBase(fixtures.BaseTestFixture):

    """Child class of fixtures.BaseTestFixture for testing CDN.

    Inherit from this and write your test methods. If the child class defines
    a prepare(self) method, this method will be called before executing each
    test method.
    """

    @classmethod
    def setUpClass(cls):

        super(TestBase, cls).setUpClass()

        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()

        cls.auth_config = config.AuthConfig()
        if cls.auth_config.auth_enabled:
            cls.auth_client = client.AuthClient()
            auth_token, cls.user_project_id = \
                cls.auth_client.authenticate_user(
                    cls.auth_config.base_url,
                    cls.auth_config.user_name,
                    cls.auth_config.api_key,
                    cls.auth_config.password)
        else:
            auth_token = str(uuid.uuid4())
            cls.user_project_id = str(uuid.uuid4())

        cls.test_config = config.TestConfig()

        cls.config = config.PoppyConfig()
        if cls.test_config.project_id_in_url:
            cls.url = cls.config.base_url + '/v1.0/' + cls.user_project_id
        else:
            cls.url = cls.config.base_url + '/v1.0'

        cls.client = client.PoppyClient(cls.url, auth_token,
                                        cls.user_project_id,
                                        serialize_format='json',
                                        deserialize_format='json')

        if cls.auth_config.multi_user:
            alt_auth_token, alt_project_id = cls.auth_client.authenticate_user(
                cls.auth_config.base_url,
                cls.auth_config.alt_user_name,
                cls.auth_config.alt_api_key)
            if cls.test_config.project_id_in_url:
                alt_url = cls.config.base_url + '/v1.0/' + alt_project_id
            else:
                alt_url = cls.config.base_url + '/v1.0'

            cls.alt_user_client = client.PoppyClient(
                alt_url, alt_auth_token,
                alt_project_id,
                serialize_format='json',
                deserialize_format='json')

            service_limit_auth_token, service_limit_project_id = \
                cls.auth_client.authenticate_user(
                    cls.auth_config.base_url,
                    cls.auth_config.service_limit_user_name,
                    cls.auth_config.service_limit_api_key)
            if cls.test_config.project_id_in_url:
                service_limit_url = cls.config.base_url \
                    + '/v1.0/' + service_limit_project_id
            else:
                service_limit_url = cls.config.base_url + '/v1.0'

            cls.service_limit_user_client = client.PoppyClient(
                service_limit_url, service_limit_auth_token,
                service_limit_project_id,
                serialize_format='json',
                deserialize_format='json')
        if cls.test_config.run_operator_tests:
            operator_auth_token, operator_project_id = \
                cls.auth_client.authenticate_user(
                    cls.auth_config.base_url,
                    cls.auth_config.operator_user_name,
                    cls.auth_config.operator_api_key)
            if cls.test_config.project_id_in_url:
                cls.operator_url = cls.config.base_url + '/v1.0/' + \
                    operator_project_id
            else:
                cls.operator_url = cls.config.base_url + '/v1.0'

            cls.operator_client = client.PoppyClient(
                cls.operator_url, operator_auth_token, operator_project_id,
                serialize_format='json',
                deserialize_format='json')

            cls.dns_config = config.DNSConfig()
            cls.shared_ssl_num_shards = cls.dns_config.shared_ssl_num_shards
            cls.dns_client = client.DNSClient(cls.dns_config.dns_username,
                                              cls.dns_config.dns_api_key)

            cls.akamai_config = config.AkamaiConfig()

    def generate_random_string(self, prefix='API-Tests', length=12):
        """Generates a random string of given prefix & length"""
        random_string = ''.join(random.choice(
            string.ascii_lowercase + string.digits)
            for _ in range(length))
        random_string = prefix + random_string
        return random_string

    def assertSchema(self, response_json, expected_schema):
        """Verify response schema aligns with the expected schema."""
        try:
            jsonschema.validate(response_json, expected_schema)
        except jsonschema.ValidationError as message:
            assert False, message

    @property
    def test_flavor(self):
        if self.test_config.generate_flavors:
            provider_name = self.test_config.generated_provider
            # create the flavor
            flavor_id = str(uuid.uuid1())
            self.client.create_flavor(
                flavor_id=flavor_id,
                provider_list=[{
                    "provider": provider_name,
                    "links": [{"href": "www.{0}.com".format(provider_name),
                               "rel": "provider_url"}]}])
        else:
            flavor_id = self.test_config.default_flavor

        return flavor_id

    def setup_service(self, service_name, domain_list, origin_list,
                      caching_list=[], restrictions_list=[], flavor_id=None,
                      log_delivery=False):
        resp = self.client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            restrictions_list=restrictions_list,
            flavor_id=flavor_id,
            log_delivery=log_delivery)

        self.assertEqual(resp.status_code, 202, msg=resp.text)
        self.service_location = resp.headers['location']
        self.client.wait_for_service_status(
            location=self.service_location,
            status='DEPLOYED',
            abort_on_status='FAILED',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        return resp

    def _service_limit_create_test_service(self, client, resp_code=False):
        service_name = str(uuid.uuid1())

        domain_list = [{"domain": self.generate_random_string(
            prefix='www.api-test-domain') + '.com'}]

        origin_list = [{"origin": self.generate_random_string(
            prefix='api-test-origin') + '.com', "port": 80, "ssl": False,
            "hostheadertype": "custom", "hostheadervalue":
            "www.customweb.com"}]
        caching_list = [
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
        log_delivery = {"enabled": False}

        resp = client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_id=self.flavor_id,
            log_delivery=log_delivery)

        if resp_code:
            return resp

        self.assertEqual(resp.status_code, 202)
        service_url = resp.headers["location"]
        client.wait_for_service_status(
            location=service_url,
            status='DEPLOYED',
            abort_on_status='FAILED',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

        return service_url

    def assert_patch_service_details(self, actual_response, expected_response):
        self.assertEqual(actual_response['name'],
                         expected_response['name'])
        self.assertEqual(sorted(actual_response['origins']),
                         sorted(expected_response['origins']))
        self.assertEqual(sorted(actual_response['caching']),
                         sorted(expected_response['caching']))
        self.assertEqual(sorted(actual_response['restrictions']),
                         sorted(expected_response['restrictions']))
        self.assertEqual(actual_response['flavor_id'],
                         expected_response['flavor_id'])

        for item in actual_response['domains']:
            if item['protocol'] == 'https':
                matched_domain_in_body = next(b_item for b_item
                                              in expected_response['domains']
                                              if (
                                                  b_item['domain'] ==
                                                  item['domain'])
                                              or (b_item.get('certificate') ==
                                                  'shared' and
                                                  item['domain'].split('.')[0]
                                                  == b_item['domain']))
                if item['certificate'] == 'shared':
                    matched_domain_in_body['domain'] = item['domain']
                matched_domain_in_body["certificate_status"] = (
                    item["certificate_status"])
        self.assertEqual(sorted(actual_response['domains']),
                         sorted(expected_response['domains']))

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
