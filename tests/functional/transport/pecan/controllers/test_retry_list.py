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

import uuid

import ddt

from tests.functional.transport.pecan import base


@ddt.ddt
class TestRetryList(base.FunctionalTest):

    def setUp(self):
        super(TestRetryList, self).setUp()

        self.project_id = str(uuid.uuid1())

    def test_get_retry_list(self):
        response = self.app.get('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                headers={
                                    'X-Project-ID': self.project_id})
        self.assertEqual(200, response.status_code)
