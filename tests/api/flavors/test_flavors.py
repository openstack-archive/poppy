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

import ddt

from tests.api import base
from tests.api.utils.schema import response


@ddt.ddt
class TestCreateFlavors(base.TestBase):

    """Tests for Flavors."""

    def setUp(self):
        super(TestCreateFlavors, self).setUp()
        self.flavor_id = str(uuid.uuid1())

    @ddt.file_data('data_create_flavor.json')
    def test_create_flavor(self, test_data):

        #self.skipTest('Endpoint Not Implemented')

        provider_list = test_data['provider_list']

        resp = self.client.create_flavor(flavor_id=self.flavor_id,
                                         provider_list=provider_list)
        self.assertEqual(resp.status_code, 204)

        # Get on Created Flavor
        location = resp.headers['location']
        resp = self.client.get_flavor(flavor_location=location)
        self.assertEqual(resp.status_code, 200)

        response_body = resp.json()
        self.assertSchema(response_body, response.get_flavor)
        self.assertEqual(response_body['provider'], provider_list)

    def tearDown(self):
        self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestCreateFlavors, self).tearDown()


@ddt.ddt
class TestFlavorActions(base.TestBase):

    """Tests for GET & DELETE Flavors."""

    def setUp(self):
        super(TestFlavorActions, self).setUp()
        self.flavor_id = str(uuid.uuid1())
        self.provider_list = []
        self.client.create_flavor(flavor_id=self.flavor_id,
                                  provider_list=self.provider_list)

    def test_get_flavor(self):
        #self.skipTest('Endpoint Not Implemented')

        resp = self.client.get_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 200)

        response_body = resp.json()
        self.assertSchema(response_body, response.get_flavor)
        self.assertEqual(response_body['provider'], self.provider_list)

    def test_delete_flavor(self):
        #self.skipTest('Endpoint Not Implemented')

        resp = self.client.delete_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 204)

        resp = self.client.get_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 404)

    def tearDown(self):
        self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestFlavorActions, self).tearDown()
