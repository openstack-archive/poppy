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

import mock

from poppy.common import util
from tests.functional.transport.pecan import base


class TestHealth(base.FunctionalTest):

    @mock.patch('requests.get')
    def test_health(self, mock_requests):
        response_object = util.dict2obj(
            {'content': '', 'status_code': 200})
        mock_requests.return_value = response_object

        response = self.app.get('/v1.0/health')
        self.assertEqual(200, response.status_code)

    @mock.patch('requests.get')
    def test_health_storage(self, mock_requests):
        response_object = util.dict2obj(
            {'content': '', 'status_code': 200})
        mock_requests.return_value = response_object

        response = self.app.get('/v1.0/health')
        for name in response.json['storage']:
                endpoint = '/v1.0/health/storage/{0}'.format(
                    name)
                response = self.app.get(endpoint)
                self.assertEqual(200, response.status_code)
                self.assertIn('true', str(response.body))

    def test_get_unknown_storage(self):
        response = self.app.get('/v1.0/health/storage/unknown',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)

    @mock.patch('requests.get')
    def test_health_provider(self, mock_requests):
        response_object = util.dict2obj(
            {'content': '', 'status_code': 200})
        mock_requests.return_value = response_object

        response = self.app.get('/v1.0/health')
        for name in response.json['providers']:
                endpoint = '/v1.0/health/provider/{0}'.format(
                    name)
                response = self.app.get(endpoint)
                self.assertEqual(200, response.status_code)
                self.assertIn('true', str(response.body))

    def test_get_unknown_provider(self):
        response = self.app.get('/v1.0/health/provider/unknown',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
