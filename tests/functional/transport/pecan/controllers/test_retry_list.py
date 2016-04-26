# Copyright (c) 2015 Rackspace, Inc.
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

import functools
import json
import uuid

import ddt
import mock

from poppy.storage.mockdb import certificates
from tests.functional.transport.pecan import base


@ddt.ddt
class TestRetryList(base.FunctionalTest):

    def setUp(self):
        super(TestRetryList, self).setUp()

        self.project_id = str(uuid.uuid1())

    def test_get_retry_list(self):
        response = self.app.get('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                headers={
                                    'X-Project-ID': self.project_id})
        self.assertEqual(200, response.status_code)

    @ddt.file_data("data_put_retry_list_bad.json")
    def test_put_retry_list_negative(self, put_data):
        response = self.app.put('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                params=json.dumps(put_data),
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_put_retry_list_positive(self):
        put_data = [
            {
                "domain_name": "test-san1.cnamecdn.com",
                "project_id": "000",
                "flavor_id": "premium",
                "validate_service": False
            },
            {
                "domain_name": "test-san2.cnamecdn.com",
                "project_id": "000",
                "flavor_id": "premium",
                "validate_service": False
            }
        ]
        response = self.app.put('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                params=json.dumps(put_data),
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                )
        self.assertEqual(200, response.status_code)

    def test_put_retry_list_negative_with_validate_service(self):
        put_data = [
            {
                "domain_name": "test-san1.cnamecdn.com",
                "project_id": "000",
                "flavor_id": "premium",
                "validate_service": False
            },
            {
                "domain_name": "test-san2.cnamecdn.com",
                "project_id": "000",
                "flavor_id": "premium",
                "validate_service": True
            }
        ]
        response = self.app.put('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                params=json.dumps(put_data),
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_put_retry_list_negative_with_deployed_domain(self):
        # A cert already in deployed status will cause 400.
        with mock.patch('poppy.storage.mockdb.certificates.'
                        'CertificatesController.get_certs_by_domain',
                        new=functools.
                        partial(certificates.CertificatesController.
                                get_certs_by_domain,
                                status='deployed')):
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

            # create a service with the domain_name test-san2.cnamecdn.com
            self.service_json = {
                "name": self.service_name,
                "domains": [
                    {"domain": "test-san2.cnamecdn.com",
                     "protocol": "https",
                     "certificate": "san"}
                ],
                "origins": [
                    {
                        "origin": "mocksite.com",
                    }
                ],
                "flavor_id": self.flavor_id,
            }

            response = self.app.post('/v1.0/services',
                                     params=json.dumps(self.service_json),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'X-Project-ID': self.project_id})
            self.assertEqual(202, response.status_code)

            put_data = [
                {
                    "domain_name": "test-san1.cnamecdn.com",
                    "project_id": "000",
                    "flavor_id": "premium",
                    "validate_service": False
                },
                {
                    "domain_name": "test-san2.cnamecdn.com",
                    "project_id": "000",
                    "flavor_id": "premium",
                    "validate_service": True
                }
            ]
            response = self.app.put('/v1.0/admin/provider/akamai/'
                                    'ssl_certificate/retry_list',
                                    params=json.dumps(put_data),
                                    headers={
                                        'Content-Type': 'application/json',
                                        'X-Project-ID': self.project_id},
                                    expect_errors=True)
            self.assertEqual(400, response.status_code)

    def test_put_retry_list_positive_with_validate_service(self):
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

        # create a service with the domain_name test-san2.cnamecdn.com
        self.service_json = {
            "name": self.service_name,
            "domains": [
                {"domain": "test-san2.cnamecdn.com",
                 "protocol": "https",
                 "certificate": "san"}
            ],
            "origins": [
                {
                    "origin": "mocksite.com",
                }
            ],
            "flavor_id": self.flavor_id,
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(self.service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)

        # This time the service is present, so the request goes through
        put_data = [
            {
                "domain_name": "test-san1.cnamecdn.com",
                "project_id": "000",
                "flavor_id": "premium",
                "validate_service": False
            },
            {
                "domain_name": "test-san2.cnamecdn.com",
                "project_id": self.project_id,
                "flavor_id": "premium",
                "validate_service": True
            }
        ]
        response = self.app.put('/v1.0/admin/provider/akamai/'
                                'ssl_certificate/retry_list',
                                params=json.dumps(put_data),
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                )
        self.assertEqual(200, response.status_code)

    def test_post_retry_list(self):
        response = self.app.post('/v1.0/admin/provider/akamai/'
                                 'ssl_certificate/retry_list',
                                 headers={
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)
