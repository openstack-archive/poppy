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

import json
import uuid

from tests.functional.transport.pecan import base


class TestServicesAction(base.FunctionalTest):

    def test_services_action_with_bad_input(self):
        # missing action field
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1())
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 }, expect_errors=True)

        self.assertEqual(response.status_code, 400)

    def test_services_action_enable(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'action': 'enable'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 })

        self.assertEqual(response.status_code, 202)

    def test_services_action_disable(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'action': 'disable'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 })

        self.assertEqual(response.status_code, 202)
