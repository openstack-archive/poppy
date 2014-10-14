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

import ddt
from oslo.config import cfg
import pecan
from webtest import app

from poppy.transport.pecan.controllers import base as c_base
from tests.functional.transport.pecan import base

LIMITS_OPTIONS = [
    cfg.IntOpt('max_services_per_page', default=20,
               help='Max number of services per page for list services'),
]

LIMITS_GROUP = 'drivers:transport:limits'


@ddt.ddt
class ServiceControllerTest(base.FunctionalTest):

    def test_get_all(self):
        response = self.app.get('/v1.0/0001/services', params={
            "marker": 2,
            "limit": 3
        })

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
        response = self.app.get('/v1.0/0001/services/fake_service_name')

        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.body.decode("utf-8"))
        self.assertTrue("domains" in response_dict)
        self.assertTrue("origins" in response_dict)

    def test_get_one_not_exist(self):
        self.assertRaises(app.AppError, self.app.get,
                          '/v1.0/0001/services/non_exist_service_name')

    @ddt.file_data("data_create_service.json")
    def test_create(self, service_json):
        # create with good data
        response = self.app.post('/v1.0/0001/services',
                                 params=json.dumps(service_json),
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(202, response.status_code)

    @ddt.file_data("data_create_service_bad_input_json.json")
    def test_create_with_bad_input_json(self, service_json):
        # create with errorenous data: invalid json data
        self.assertRaises(app.AppError, self.app.post,
                          '/v1.0/0001/services',
                          params="{", headers={
                              "Content-Type": "application/json"
                          })

        # create with errorenous data
        self.assertRaises(app.AppError, self.app.post,
                          '/v1.0/0001/services',
                          params=json.dumps(service_json), headers={
                              "Content-Type": "application/json"
                          })

    def test_update(self):
        # update with erroneous data
        self.assertRaises(app.AppError, self.app.patch,
                          '/v1.0/0001/services/fake_service_name_3',
                          params=json.dumps({
                              "origins": [
                                  {
                                      # missing "origin" here
                                      "port": 80,
                                      "ssl": False
                                  }
                              ]
                          }), headers={
                              "Content-Type": "application/json"
                          })

        # update with good data
        response = self.app.patch('/v1.0/0001/services/fake_service_name_3',
                                  params=json.dumps({
                                      "origins": [
                                          {
                                                    "origin": "44.33.22.11",
                                                    "port": 80,
                                                    "ssl": False
                                                    }
                                      ]
                                  }), headers={
                                      "Content-Type": "application/json"
                                  })
        self.assertEqual(200, response.status_code)

    def test_patch_non_exist(self):
        # This is for coverage 100%
        self.assertRaises(app.AppError, self.app.patch, "/v1.0/0001",
                          headers={
                              "Content-Type": "application/json"
                          })

        self.assertRaises(app.AppError, self.app.patch,
                          "/v1.0/01234/123",
                          headers={
                              "Content-Type": "application/json"
                          })

        class FakeController(c_base.Controller):

            @pecan.expose("json")
            def patch_all(self):
                return "Hello World!"

        self.test_fake_controller = FakeController(None)
        patch_ret_val = self.test_fake_controller._handle_patch('patch', '')
        self.assertTrue(len(patch_ret_val) == 2)

    def test_delete(self):
        response = self.app.delete('/v1.0/0001/services/fake_service_name_4')

        self.assertEqual(202, response.status_code)

    def test_delete_non_eixst(self):
        self.assertRaises(app.AppError, self.app.delete,
                          '/v1.0/0001/services/non_exist_service_name'
                          )
