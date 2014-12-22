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

import ddt
from nose.plugins import attrib

from tests.api import base


@ddt.ddt
class TestMultiUser(base.TestBase):

    """Tests involving multiple user accounts."""

    def setUp(self):
        super(TestMultiUser, self).setUp()

    @attrib.attr('smoke')
    def test_ping(self):

        resp = self.client.ping()
        self.assertEqual(resp.status_code, 204)

        alt_user_resp = self.alt_user_client.ping()
        self.assertEqual(alt_user_resp.status_code, 401)

    def tearDown(self):
        super(TestMultiUser, self).tearDown()
