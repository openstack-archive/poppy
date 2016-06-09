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

from tests.api import base


class TestGetSetSanMappingList(base.TestBase):

    def setUp(self):
        super(TestGetSetSanMappingList, self).setUp()

    def test_get_san_mapping_positive(self):
        resp = self.client.get_san_mapping_list()

        self.assertEqual(resp.status_code, 200)

    def test_update_san_cert_positive(self):
        resp = self.client.put_san_mapping_list(
            [
                {
                    "domain_name": "www.example.com",
                    "flavor_id": "flavor_id",
                    "project_id": "project_id",
                    "cert_type": "san",
                    "cert_details": {
                        "Akamai": {
                            "extra_info": {
                                "san cert": "san.example.com",
                                "akamai_spsId": 1
                            }
                        }
                    }
                }
            ]
        )

        self.assertEqual(resp.status_code, 200)

    def test_update_san_cert_negative(self):
        resp = self.client.put_san_mapping_list(
            [
                {
                    "san_cert_name": "san.example.com"
                }
            ]
        )

        self.assertEqual(resp.status_code, 400)
