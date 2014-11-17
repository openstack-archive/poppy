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

import ddt
import mock

from poppy.common import uri
from poppy.manager.default import flavors as manager
from poppy.transport.pecan.models.request import flavor
from tests.functional.transport.pecan import base


@ddt.ddt
class FlavorControllerTest(base.FunctionalTest):

    def setUp(self):
        super(FlavorControllerTest, self).setUp()

        self.project_id = str(uuid.uuid1())

    def test_get_all(self):
        response = self.app.get('/v1.0/flavors',
                                headers={'X-Project-ID': self.project_id})
        self.assertEqual(200, response.status_code)

    @ddt.file_data('data_create_flavor.json')
    @mock.patch.object(manager.DefaultFlavorsController, 'storage')
    def test_get_one(self, value, mock_manager):

        return_flavor = flavor.load_from_json(value)

        # mock the storage response
        mock_response = return_flavor
        mock_manager.get.return_value = mock_response

        url = u'/v1.0/flavors/{0}'.format(uri.encode(value['id']))
        response = self.app.get(url, headers={'X-Project-ID': self.project_id})

        self.assertEqual(200, response.status_code)

    def test_get_not_found(self):
        response = self.app.get('/v1.0/flavors/{0}'.format("non_exist"),
                                headers={'X-Project-ID': self.project_id},
                                status=404,
                                expect_errors=True)

        self.assertEqual(404, response.status_code)

    @ddt.file_data('data_create_flavor_bad.json')
    def test_create_bad_data(self, value):

        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(value),
                                 headers={
                                     "Content-Type": "application/json",
                                     'X-Project-ID': self.project_id},
                                 status=400,
                                 expect_errors=True)

        self.assertEqual(400, response.status_code)

    @ddt.file_data('data_create_flavor.json')
    @mock.patch.object(manager.DefaultFlavorsController, 'storage')
    def test_create_exception(self, value, mock_storage):
        mock_storage.add.side_effect = Exception()

        # create with good data
        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(value),
                                 headers={
                                     "Content-Type": "application/json",
                                     'X-Project-ID': self.project_id},
                                 expect_errors=True)

        self.assertEqual(400, response.status_code)

    @ddt.file_data('data_create_flavor.json')
    def test_create(self, value):
        value['id'] = u'{0}_{1}'.format(value['id'], uuid.uuid1())

        # create with good data
        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(value),
                                 headers={
                                     "Content-Type": "application/json",
                                     'X-Project-ID': self.project_id})
        self.assertEqual(201, response.status_code)

    def test_delete(self):
        response = self.app.delete(
            '/v1.0/flavors/{0}'.format(uuid.uuid1()),
            headers={'X-Project-ID': self.project_id}
        )

        self.assertEqual(204, response.status_code)
