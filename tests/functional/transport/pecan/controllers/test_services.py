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

from tests.functional.transport.pecan import base


class ServiceControllerTest(base.FunctionalTest):

    def test_get_all(self):
        response = self.app.get('/v1.0/0001/services', params={
                                    "marker" : 2,
                                    "limit" : 3
                                })

        self.assertEqual(200, response.status_code)
    
    def test_get_one(self):
        response = self.app.get('/v1.0/0001/services/fake_service_name')

        self.assertEqual(200, response.status_code)
    
    def test_create(self):
        response = self.app.put('/v1.0/0001/services/fake_service_name_2', 
                                params=json.dumps({
                                    "domain": "www.mytest.com"
                                }), headers = {
                                  "Content-Type" : "application/json"
                               })

        self.assertEqual(200, response.status_code)
    
    def test_update(self):
        response = self.app.patch('/v1.0/0001/services/fake_service_name_3',
                                   params=json.dumps({
                                    "domain": "www.mytest.com"
                                    }), headers = {
                                  "Content-Type" : "application/json"
                                  })

        self.assertEqual(200, response.status_code)
        
    def test_delete(self):
        response = self.app.delete('/v1.0/0001/services/fake_service_name_4')

        self.assertEqual(200, response.status_code)