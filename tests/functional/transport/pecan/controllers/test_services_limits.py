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

import six.moves.urllib_parse as urlparse


class TestServicesLimit(base.FunctionalTest):

    def test_services_limit_with_bad_input(self):
        # missing limits field
        response = self.app.post('/v1.0/admin/limits',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1())
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid4())
                                 }, expect_errors=True)

        self.assertEqual(response.status_code, 400)
        # invalid limits field
        response = self.app.post('/v1.0/admin/limits',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'limits': -5
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid4())
                                 }, expect_errors=True)

        self.assertEqual(response.status_code, 400)
        # invalid projectid field
        response = self.app.post('/v1.0/admin/limits',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()) * 50,
                                     'limits': 10
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid4())
                                 }, expect_errors=True)

        self.assertEqual(response.status_code, 400)

    def test_services_limit_with_good_input(self):
        # valid limits and project_id field
        project_id = str(uuid.uuid1())
        response = self.app.post('/v1.0/admin/limits',
                                 params=json.dumps({
                                     'project_id': project_id,
                                     'limit': 10
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid4())
                                 }, expect_errors=True)
        self.assertEqual(response.status_code, 202)

        path = '/v1.0/admin/limits/{0}'.format(project_id)
        parsed_location = urlparse.urlparse(response.headers['Location'])

        self.assertEqual(parsed_location.path, path)
