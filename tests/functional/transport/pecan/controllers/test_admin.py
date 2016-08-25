# Copyright (c) 2016 Rackspace, Inc.
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


class AdminControllerTest(base.FunctionalTest):

    def setUp(self):
        super(AdminControllerTest, self).setUp()

        self.project_id = str(uuid.uuid1())

    def tearDown(self):
        super(AdminControllerTest, self).tearDown()

    def test_put_settings_positive(self):
        settings_json = {
            'san_cert_hostname_limit': 10
        }

        # create with good data
        response = self.app.post(
            '/v1.0/admin/provider/akamai/ssl_certificate/'
            'config/san_cert_hostname_limit',
            params=json.dumps(settings_json),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            }
        )
        self.assertEqual(202, response.status_code)

    def test_put_akamai_settings_negative(self):
        settings_json = {
            'san_cert_hostname_limit': 10
        }

        # create with bad endpoint which fails validation with 400 error
        response = self.app.post(
            '/v1.0/admin/provider/akamai/ssl_certificate/'
            'config/unknown_setting',
            params=json.dumps(settings_json),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_get_settings_positive(self):
        response = self.app.get(
            '/v1.0/admin/provider/akamai/ssl_certificate/'
            'config/san_cert_hostname_limit',
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            }
        )
        self.assertEqual(200, response.status_code)

    def test_get_akamai_settings_negative(self):
        response = self.app.get(
            '/v1.0/admin/provider/akamai/ssl_certificate/'
            'config/unknown_setting',
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_post_background_job_negative(self):
        response = self.app.post(
            '/v1.0/admin/provider/akamai/background_job',
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            params=json.dumps([]),
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_post_service_status_negative(self):
        response = self.app.post(
            '/v1.0/admin/services/status',
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            params=json.dumps([]),
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_post_migrate_domain_invalid_domain_name(self):
        payload = {
            "project_id": self.project_id,
            "service_id": "abcdef",
            "domain_name": "invalid",
            "new_cert": "scdn1.secure6.raxcdn.com.edgekey.net",
            "cert_status": "create_in_progress"
        }

        # post with bad data
        response = self.app.post(
            '/v1.0/admin/provider/akamai/service',
            params=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_post_migrate_domain_non_existant_service(self):
        payload = {
            "project_id": self.project_id,
            "service_id": "does_not_exist",
            "domain_name": "www.test.com",
            "new_cert": "scdn1.secure6.raxcdn.com",
            "cert_status": "create_in_progress"
        }

        response = self.app.post(
            '/v1.0/admin/provider/akamai/service',
            params=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(404, response.status_code)

    def test_post_migrate_domain_new_cert_with_edge_key(self):
        payload = {
            "project_id": self.project_id,
            "service_id": "does_not_exist",
            "domain_name": "www.test.com",
            "new_cert": "scdn1.secure6.raxcdn.com.edgekey.net",
            "cert_status": "create_in_progress"
        }

        response = self.app.post(
            '/v1.0/admin/provider/akamai/service',
            params=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(404, response.status_code)
