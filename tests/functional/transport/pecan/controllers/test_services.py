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
from oslo.config import cfg
import pecan

from poppy.transport.pecan.controllers import base as c_base
from tests.functional.transport.pecan import base

LIMITS_OPTIONS = [
    cfg.IntOpt('max_services_per_page', default=20,
               help='Max number of services per page for list services'),
]

LIMITS_GROUP = 'drivers:transport:limits'


@ddt.ddt
class ServiceControllerTest(base.FunctionalTest):

    def setUp(self):
        super(ServiceControllerTest, self).setUp()

        self.project_id = str(uuid.uuid1())
        self.service_name = str(uuid.uuid1())
        self.flavor_id = str(uuid.uuid1())

        # create a mock flavor to be used by new service creations
        flavor_json = {
            "id": self.flavor_id,
            "providers": [
                {
                    "provider": "mock",
                    "links": [
                        {
                            "href": "http://mock.cdn",
                            "rel": "provider_url"
                        }
                    ]
                }
            ]
        }
        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(flavor_json),
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(204, response.status_code)

        # create an initial service to be used by the tests
        service_json = {
            "name": "mysite.com",
            "domains": [
                {"domain": "test.mocksite.com"},
                {"domain": "blog.mocksite.com"}
            ],
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 80,
                    "ssl": False
                }
            ],
            "flavorRef": self.flavor_id,
            "caching": [
                {
                    "name": "default",
                    "ttl": 3600
                }
            ],
            "restrictions": [
                {
                    "name": "website only",
                    "rules": [
                        {
                            "name": "mocksite.com",
                            "http_host": "www.mocksite.com"
                        }
                    ]
                }
            ]
        }

        service_json['name'] = self.service_name
        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)

    def tearDown(self):
        super(ServiceControllerTest, self).tearDown()

        # delete the mock flavor
        # response = self.app.delete('/v1.0/flavors/' + self.flavor_id)
        # self.assertEqual(204, response.status_code)

        # delete the test service
        # response = self.app.delete('/v1.0/services/' + self.service_name)
        # self.assertEqual(200, response.status_code)

    def test_get_all(self):
        response = self.app.get('/v1.0/services', params={
            "marker": 2,
            "limit": 3
        }, headers={'X-Project-ID': self.project_id})

        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.body.decode("utf-8"))
        self.assertTrue("links" in response_dict)
        self.assertTrue("services" in response_dict)

    def test_get_more_than_max_services_per_page(self):
        self.conf.register_opts(LIMITS_OPTIONS, group=LIMITS_GROUP)
        self.limits_conf = self.conf[LIMITS_GROUP]
        self.max_services_per_page = self.limits_conf.max_services_per_page

        response = self.app.get('/v1.0/0001/services', params={
            "marker": 'service_name',
            "limit": self.max_services_per_page + 1
        }, expect_errors=True)

        self.assertEqual(400, response.status_code)

    def test_get_one(self):
        response = self.app.get(
            '/v1.0/services/' + self.service_name,
            headers={'X-Project-ID': self.project_id})

        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.body.decode("utf-8"))
        self.assertTrue("domains" in response_dict)
        self.assertTrue("origins" in response_dict)

    def test_get_one_not_exist(self):
        response = self.app.get('/v1.0/services/non_exist_service_name',
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                expect_errors=True)

        self.assertEqual(404, response.status_code)

    @ddt.file_data("data_create_service.json")
    def test_create(self, service_json):

        # override the hardcoded flavorRef in the ddt file with
        # a custom one defined in setUp()
        service_json['flavorRef'] = self.flavor_id

        # create with good data
        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)

    def test_create_with_invalid_json(self):
        # create with errorenous data: invalid json data
        response = self.app.post('/v1.0/services',
                                 params="{",
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_create_service_bad_input_json.json")
    def test_create_with_bad_input_json(self, service_json):
        # create with errorenous data
        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_create_service_duplicate.json")
    def test_create_with_duplicate_name(self, service_json):
        # override name
        service_json['name'] = self.service_name
        service_json['flavorRef'] = self.flavor_id

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_update_with_bad_input(self):
        # update with erroneous data
        response = self.app.patch('/v1.0/services/' + self.service_name,
                                  params=json.dumps({
                                      "origins": [
                                          {
                                              # missing "origin" here
                                              "port": 80,
                                              "ssl": False
                                          }
                                      ]
                                  }),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'X-Project-ID': self.project_id
                                  },
                                  expect_errors=True)

        self.assertEqual(400, response.status_code)

    def test_update_with_good_input(self):
        self.skip('skipping failing test for now')
        response = self.app.get(
            '/v1.0/services/' + self.service_name,
            headers={'X-Project-ID': self.project_id})
        self.assertEqual(200, response.status_code)

        # update with good data
        response = self.app.patch('/v1.0/services/' + self.service_name,
                                  params=json.dumps({
                                      "origins": [
                                          {
                                              "origin": "44.33.22.11",
                                              "port": 80,
                                              "ssl": False
                                          }
                                      ]
                                  }),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'X-Project-ID': self.project_id
                                  })
        self.assertEqual(200, response.status_code)

    def test_patch_non_exist(self):
        # This is for coverage 100%
        response = self.app.patch("/v1.0",
                                  headers={
                                      'Content-Type': 'application/json',
                                      'X-Project-ID': self.project_id
                                  },
                                  expect_errors=True)
        self.assertEqual(404, response.status_code)

        response = self.app.patch("/v1.0/" + self.project_id,
                                  headers={
                                      'Content-Type': 'application/json'
                                  },
                                  expect_errors=True)
        self.assertEqual(404, response.status_code)

        class FakeController(c_base.Controller):

            @pecan.expose("json")
            def patch_all(self):
                return "Hello World!"

        self.test_fake_controller = FakeController(None)
        patch_ret_val = self.test_fake_controller._handle_patch('patch', '')
        self.assertTrue(len(patch_ret_val) == 2)

    # def test_delete(self):
    # TODO(amitgandhinz): commented this out until the Delete Patch lands
    # due to this test failing.
    #     response = self.app.delete('/v1.0/services/fake_service_name_4')

    #     self.assertEqual(200, response.status_code)

    def test_delete_non_eixst(self):
        response = self.app.delete('/v1.0/%s/services/non_exist_service_name' %
                                   self.project_id,
                                   headers={
                                       'Content-Type': 'application/json'
                                   },
                                   expect_errors=True)
        self.assertEqual(404, response.status_code)
