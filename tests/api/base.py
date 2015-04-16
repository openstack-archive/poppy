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

        cls.auth_config = config.AuthConfig()
        if cls.auth_config.auth_enabled:
            cls.auth_client = client.AuthClient()
            auth_token, project_id = cls.auth_client.authenticate_user(
                cls.auth_config.base_url,
                cls.auth_config.user_name,
                cls.auth_config.api_key)
        else:
            auth_token = str(uuid.uuid4())
            project_id = str(uuid.uuid4())

        cls.test_config = config.TestConfig()

        cls.config = config.PoppyConfig()
        if cls.test_config.project_id_in_url:
            cls.url = cls.config.base_url + '/v1.0/' + project_id
        else:
            cls.url = cls.config.base_url + '/v1.0'

        cls.client = client.PoppyClient(cls.url, auth_token, project_id,
                                        serialize_format='json',
                                        deserialize_format='json')

        if cls.auth_config.multi_user:
            alt_auth_token, alt_project_id = cls.auth_client.authenticate_user(
                cls.auth_config.base_url,
                cls.auth_config.alt_user_name,
                cls.auth_config.alt_api_key)
            if cls.test_config.project_id_in_url:
                cls.alt_url = cls.config.base_url + '/v1.0/' + alt_project_id
            else:
                cls.alt_url = cls.config.base_url + '/v1.0'

            cls.alt_user_client = client.PoppyClient(
                cls.alt_url, alt_auth_token,
                alt_project_id,
                serialize_format='json',
                deserialize_format='json')

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

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
