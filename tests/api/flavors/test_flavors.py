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
from nose.plugins import attrib

from tests.api import base
from tests.api.utils.schema import flavors


@ddt.ddt
class TestCreateFlavors(base.TestBase):

    """Tests for Flavors."""

    def setUp(self):
        super(TestCreateFlavors, self).setUp()
        self.flavor_id = str(uuid.uuid1())

    @ddt.file_data('data_create_flavor.json')
    def test_create_flavor(self, test_data):

        provider_list = test_data['provider_list']
        limits = test_data['limits']

        if 'flavor_id' in test_data:
            self.flavor_id = test_data['flavor_id']
        flavor_id = self.flavor_id

        resp = self.client.create_flavor(flavor_id=flavor_id,
                                         provider_list=provider_list,
                                         limits=limits)
        self.assertEqual(resp.status_code, 201)

        # Get on Created Flavor
        location = resp.headers['location']
        resp = self.client.get_flavor(flavor_location=location)
        self.assertEqual(resp.status_code, 200)

        response_body = resp.json()
        self.assertSchema(response_body, flavors.get_flavor)
        self.assertEqual(sorted(response_body['providers']),
                         sorted(provider_list))

    @ddt.file_data('data_create_flavor_negative.json')
    def test_create_flavor_negative_tests(self, test_data):
        if 'skip_test' in test_data:
            self.skipTest('Not Implemented - bp# post-flavors-error-handling')

        provider_list = test_data['provider_list']
        limits = test_data['limits']

        if 'flavor_id' in test_data:
            flavor_id = test_data['flavor_id']
        else:
            flavor_id = self.flavor_id

        resp = self.client.create_flavor(flavor_id=flavor_id,
                                         provider_list=provider_list,
                                         limits=limits)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestCreateFlavors, self).tearDown()


@ddt.ddt
class TestFlavorActions(base.TestBase):

    """Tests for GET & DELETE Flavors."""

    def setUp(self):
        super(TestFlavorActions, self).setUp()
        self.flavor_id = str(uuid.uuid1())
        self.provider_list = [
            {"provider": "fastly",
             "links": [{"href": "http://www.fastly.com",
                        "rel": "provider_url"}]}]
        self.client.create_flavor(flavor_id=self.flavor_id,
                                  provider_list=self.provider_list)

    @attrib.attr('smoke')
    def test_get_flavor(self):

        resp = self.client.get_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 200)

        response_body = resp.json()
        self.assertSchema(response_body, flavors.get_flavor)
        self.assertEqual(response_body['providers'], self.provider_list)

    def test_delete_flavor(self):

        resp = self.client.delete_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 204)

        resp = self.client.get_flavor(flavor_id=self.flavor_id)
        self.assertEqual(resp.status_code, 404)

    def tearDown(self):
        self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestFlavorActions, self).tearDown()
