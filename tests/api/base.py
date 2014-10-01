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

import os

from cafe.drivers.unittest import fixtures
import jsonschema
from oslo.config import cfg

from tests.api.utils import client
from tests.api.utils import config
from tests.api.utils import server


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
            auth_token = cls.auth_client.get_auth_token(
                cls.auth_config.base_url,
                cls.auth_config.user_name,
                cls.auth_config.api_key)
        else:
            auth_token = 'dummy'

        cls.config = config.PoppyConfig()
        cls.url = cls.config.base_url

        cls.client = client.PoppyClient(cls.url, auth_token,
                                        serialize_format='json',
                                        deserialize_format='json')

        cls.test_config = config.TestConfig()
        if cls.test_config.run_server:
            conf_file = 'poppy_cassandra.conf'
            conf_path = os.environ["POPPY_TESTS_CONFIGS_DIR"]
            config_file = os.path.join(conf_path, conf_file)

            conf = cfg.ConfigOpts()
            conf(project='poppy', prog='poppy', args=[],
                 default_config_files=[config_file])
            cls.poppy_server = server.CDNServer()
            cls.poppy_server.start(conf)

    def assertSchema(self, response_json, expected_schema):
        """Verify response schema aligns with the expected schema."""
        try:
            jsonschema.validate(response_json, expected_schema)
        except jsonschema.ValidationError as message:
            assert False, message

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        if cls.test_config.run_server:
            cls.poppy_server.stop()
        super(TestBase, cls).tearDownClass()
