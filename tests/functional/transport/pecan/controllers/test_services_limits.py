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

import json
import uuid

from tests.functional.transport.pecan import base


class TestServicesLimit(base.FunctionalTest):

    def test_services_limits_invalid_limits(self):
        # invalid limits field
        response = self.app.put('/v1.0/admin/limits/{0}'.format(
            str(uuid.uuid1())),
            params=json.dumps({'limit': -5}),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())},
            expect_errors=True)

        self.assertEqual(response.status_code, 400)

    def test_service_limits_invalid_projectid(self):
        # invalid projectid
        response = self.app.put('/v1.0/admin/limits/{0}'.format(
            str(uuid.uuid1()) * 500),
            params=json.dumps({'limit': 10}),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())},
            expect_errors=True)

        self.assertEqual(response.status_code, 400)
