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

import json
import uuid

import ddt

from tests.functional.transport.pecan import base


@ddt.ddt
class TestSanMappingList(base.FunctionalTest):

    def setUp(self):
        super(TestSanMappingList, self).setUp()

        self.project_id = str(uuid.uuid1())

    def test_get_san_mapping_list(self):
        response = self.app.get(
            '/v1.0/admin/provider/akamai/background_job/san_mapping',
            headers={'X-Project-ID': self.project_id}
        )
        self.assertEqual(200, response.status_code)

    def test_put_san_mapping_list_negative(self):
        put_data = [
            {
                "san_cert_name": "san1.sample.com"
            }
        ]
        response = self.app.put(
            '/v1.0/admin/provider/akamai/background_job/san_mapping',
            params=json.dumps(put_data),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True
        )
        self.assertEqual(400, response.status_code)

    def test_put_san_mapping_list_positive(self):
        put_data = [
            {
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "secure1.san1.altcdn.com",
                            "akamai_spsId": 1234
                        }
                    }
                },
                "project_id": "000",
                "cert_type": "san",
                "domain_name": "www.mockssl.com",
                "flavor_id": "premium"
            }
        ]

        response = self.app.put(
            '/v1.0/admin/provider/akamai/background_job/san_mapping',
            params=json.dumps(put_data),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
        )
        self.assertEqual(200, response.status_code)
