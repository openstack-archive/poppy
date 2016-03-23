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

import random

from tests.api import base


class TestGetSetSanCertInfo(base.TestBase):

    """Tests for GET SSL Certificate."""

    def setUp(self):
        super(TestGetSetSanCertInfo, self).setUp()
        self.san_cert_name_positive = (
            self.akamai_config.san_certs_name_positive
        )

        self.san_cert_name_negative = (
            self.akamai_config.san_certs_name_negative
        )

    def test_get_san_cert_negative(self):
        resp = self.client.view_certificate_info(
            self.san_cert_name_negative
        )

        self.assertEqual(resp.status_code, 400)

    def test_get_san_cert_positive(self):
        resp = self.client.view_certificate_info(
            self.san_cert_name_positive
        )

        self.assertTrue('spsId' in resp.json())
        self.assertEqual(resp.status_code, 200)

    def test_update_san_cert(self):
        if self.test_config.run_ssl_tests is False:
            self.skipTest('Update san cert info needs to'
                          ' be run when commanded')

        resp = self.client.update_certificate_info(
            self.san_cert_name_positive,
            spsId=random.randint(1000, 2000),
            enabled=True
        )

        self.assertTrue('spsId' in resp.json())
        self.assertTrue('enabled' in resp.json())
        self.assertEqual(resp.status_code, 200)
