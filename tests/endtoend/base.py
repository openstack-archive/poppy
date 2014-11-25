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

from tests.api.utils import client
from tests.endtoend.utils import config
from tests.endtoend.utils import heatclient
from tests.endtoend.utils import wptclient


class TestBase(fixtures.BaseTestFixture):
    """Base class for End To End CDN Tests

    The tests do the following,
    1. Spins up a wordpress site on a cloud server.
    2. Create a Poppy service via API call using the origin & domain
        feom Step 1.
    3. Measures the pageload performance of the CDN enabled website.
    """

    @classmethod
    def setUpClass(cls):

        super(TestBase, cls).setUpClass()

        cls.auth_config = config.AuthConfig()
        cls.auth_client = client.AuthClient()
        auth_token, project_id = cls.auth_client.authenticate_user(
            cls.auth_config.base_url,
            cls.auth_config.user_name,
            cls.auth_config.api_key)

        cls.config = config.PoppyConfig()
        cls.url = cls.config.base_url

        cls.poppy_client = client.PoppyClient(
            cls.url, auth_token, project_id,
            serialize_format='json',
            deserialize_format='json')

        cls.test_config = config.TestConfig()

        heat_config = config.OrchestrationConfig()
        heat_url = heat_config.base_url + '/' + project_id
        cls.heat_client = heatclient.HeatClient(heat_url=heat_url,
                                                token=auth_token)

        cls.wpt_config = config.WebPageTestConfig()
        cls.wpt_client = wptclient.WebpageTestClient(
            wpt_url=cls.wpt_config.base_url, api_key=cls.wpt_config.api_key)

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
