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
            auth_token = 'dummy'
            project_id = 'dummy'

        cls.test_config = config.TestConfig()

        cls.config = config.PoppyConfig()
        if cls.test_config.project_id_in_url:
            cls.url = cls.config.base_url + '/v1.0/' + project_id
        else:
            cls.url = cls.config.base_url + '/v1.0'

        cls.client = client.PoppyClient(cls.url, auth_token, project_id,
                                        serialize_format='json',
                                        deserialize_format='json')

    def assertSchema(self, response_json, expected_schema):
        """Verify response schema aligns with the expected schema."""
        try:
            jsonschema.validate(response_json, expected_schema)
        except jsonschema.ValidationError as message:
            assert False, message

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
