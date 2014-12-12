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

import BeautifulSoup
from cafe.drivers.unittest import fixtures
import requests

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

        cls.poppy_config = config.PoppyConfig()
        cls.url = cls.poppy_config.base_url

        cls.poppy_client = client.PoppyClient(
            cls.url, auth_token, project_id,
            serialize_format='json',
            deserialize_format='json')

        cls.test_config = config.TestConfig()

        cls.heat_config = config.OrchestrationConfig()
        heat_url = cls.heat_config.base_url + '/' + project_id
        cls.heat_client = heatclient.HeatClient(heat_url=heat_url,
                                                token=auth_token)

        cls.wpt_config = config.WebPageTestConfig()
        cls.wpt_client = wptclient.WebpageTestClient(
            wpt_url=cls.wpt_config.base_url, api_key=cls.wpt_config.api_key)

    def get_content(self, url):
        """Get content from the url

        :param url: url to get content from
        :returns: content fetched from the url
        """
        response = requests.get(url)
        content = BeautifulSoup.BeautifulSoup(response.text)
        return content.findAll()

    def assertSameContent(self, origin_url, access_url):
        """Asserts that the origin & access_url serve the same content

        :param origin: Origin website
        :param access_url: CDN enabled url of the origin website
        :returns: True/False
        """
        origin_content = self.get_content(url=origin_url)
        cdn_content = self.get_content(url=access_url)
        self.assertEqual(origin_content, cdn_content)

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()
