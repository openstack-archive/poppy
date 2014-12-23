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


class ErrorHookTest(base.FunctionalTest):

    def setUp(self):
        super(ErrorHookTest, self).setUp()

        self.headers = {'X-Auth-Token': str(uuid.uuid4())}

    def test_404_error(self):
        self.headers['X-Project-Id'] = '000001'
        # use try except to actually catch the response body in
        # exception part
        service_id = str(uuid.uuid4())
        response = self.app.get(
            '/v1.0/services/' + service_id,
            headers=self.headers,
            status=404)

        self.assertEqual(404, response.status_code)
        self.assertEqual('application/json', response.content_type)
        response_json = json.loads(response.body.decode('utf-8'))
        self.assertTrue('message' in response_json)
        self.assertEqual('service {0} could not be found'.format(service_id),
                         response_json['message'])
