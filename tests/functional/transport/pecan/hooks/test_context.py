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

import uuid

from poppy.manager.default import home
from tests.functional.transport.pecan import base


class ContextHookTest(base.FunctionalTest):

    def setUp(self):
        super(ContextHookTest, self).setUp()

        self.headers = {'X-Auth-Token': str(uuid.uuid4())}

    def test_project_id_in_header(self):
        self.headers['X-Project-Id'] = str(uuid.uuid1())
        response = self.app.get('/v1.0', headers=self.headers)

        self.assertEqual(200, response.status_code)

        # Temporary until actual implementation
        self.assertEqual(home.JSON_HOME, response.json)

    def test_project_id_missing(self):
        response = self.app.get('/v1.0/',
                                headers=self.headers,
                                expect_errors=True)

        self.assertEqual(400, response.status_code)
