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

import ddt
from hypothesis import given
from hypothesis import strategies

from tests.functional.transport.pecan import base


@ddt.ddt
class TestServicesState(base.FunctionalTest):

    def setUp(self):
        super(TestServicesState, self).setUp()

        self.project_id = str(uuid.uuid4())
        self.service_id = str(uuid.uuid4())
        self.req_body = {
            'project_id': self.project_id,
            'service_id': self.service_id,
        }

    @ddt.data(u'deployed', u'failed')
    def test_services_state_valid_states(self, status):
        self.req_body['status'] = status
        response = self.app.post(
            '/v1.0/admin/services/status',
            params=json.dumps(self.req_body),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())})

        self.assertEqual(response.status_code, 201)

    @given(strategies.text())
    def test_services_state_invalid_states(self, status):
        # invalid status field
        self.req_body['status'] = status
        response = self.app.post(
            '/v1.0/admin/services/status',
            params=json.dumps(self.req_body),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())},
            expect_errors=True)

        self.assertEqual(response.status_code, 400)

    @given(strategies.text())
    def test_services_state_invalid_service_id(self, service_id):
        # invalid service_id field
        self.req_body['status'] = 'deployed'
        self.req_body['service_id'] = service_id
        response = self.app.post(
            '/v1.0/admin/services/status',
            params=json.dumps(self.req_body),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())},
            expect_errors=True)

        self.assertEqual(response.status_code, 400)

    @given(strategies.text(min_size=257))
    def test_services_state_invalid_project_id(self, project_id):
        # NOTE(TheSriram): the min size is assigned to 257, since
        # project_id regex allows upto 256 chars
        # invalid project_id field
        self.req_body['project_id'] = project_id
        self.req_body['status'] = 'deployed'
        response = self.app.post(
            '/v1.0/admin/services/status',
            params=json.dumps(self.req_body),
            headers={'Content-Type': 'application/json',
                     'X-Project-ID': str(uuid.uuid4())},
            expect_errors=True)

        self.assertEqual(response.status_code, 400)
