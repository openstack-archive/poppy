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

import ddt

from tests.functional.transport.pecan import base


@ddt.ddt
class TestHealth(base.FunctionalTest):

    def test_health(self):
        response = self.app.get('/v1.0/health')
        self.assertEqual(200, response.status_code)

    def test_health_storage(self):
        response = self.app.get('/v1.0/health/storage/mockdb')
        self.assertEqual(200, response.status_code)
        self.assertIn('true', response.body)

    def test_get_unkown_storage(self):
        response = self.app.get('/v1.0/health/storage/unknown',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)

    @ddt.file_data('data_health_provider.json')
    def test_health_provider(self, provider):
        provider_endpoint = '/v1.0/health/provider/{0}'.format(provider)
        response = self.app.get(provider_endpoint)
        self.assertEqual(200, response.status_code)
        self.assertIn('true', response.body)

    def test_get_unkown_provider(self):
        response = self.app.get('/v1.0/health/provider/unknown',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
