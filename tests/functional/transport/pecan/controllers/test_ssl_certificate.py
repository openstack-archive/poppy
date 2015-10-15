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

from tests.functional.transport.pecan import base


@ddt.ddt
class SSLCertificateControllerTest(base.FunctionalTest):

    def setUp(self):
        super(SSLCertificateControllerTest, self).setUp()

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
                                 headers={
                                     "Content-Type": "application/json",
                                     "X-Project-ID": self.project_id})

        self.assertEqual(201, response.status_code)

    @ddt.file_data("data_create_ssl_certificate.json")
    def test_create_ssl_certificate(self, ssl_certificate_json):

        # override the hardcoded flavor_id in the ddt file with
        # a custom one defined in setUp()
        ssl_certificate_json['flavor_id'] = self.flavor_id

        # create with good data
        response = self.app.post('/v1.0/ssl_certificate',
                                 params=json.dumps(ssl_certificate_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)

    def test_create_with_invalid_json(self):
        # create with errorenous data: invalid json data
        response = self.app.post('/v1.0/ssl_certificate',
                                 params="{",
                                 headers={
                                        'Content-Type': 'application/json',
                                        'X-Project-ID': self.project_id},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_create_ssl_certificate_bad_input_json.json")
    def test_create_with_bad_input_json(self, ssl_certificate_json):
        # create with errorenous data
        response = self.app.post('/v1.0/ssl_certificate',
                                 params=json.dumps(ssl_certificate_json),
                                 headers={'Content-Type': 'application/json',
                                          'X-Project-ID': self.project_id},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_cert(self):
        # create with errorenous data: invalid json data
        response = self.app.delete('/v1.0/ssl_certificate/blog.test.com',
                                   headers={'X-Project-ID': self.project_id}
                                   )
        self.assertEqual(202, response.status_code)

    def test_delete_cert_non_exist(self):
        # create with errorenous data: invalid json data
        response = self.app.delete('/v1.0/ssl_certificate/blog.non_exist.com',
                                   headers={'X-Project-ID': self.project_id},
                                   expect_errors=True)
        self.assertEqual(400, response.status_code)

    def tearDown(self):
        super(SSLCertificateControllerTest, self).tearDown()
