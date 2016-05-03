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

import ddt

from tests.api import base


@ddt.ddt
class TestCreateSSLCertificate(base.TestBase):

    """Tests for Create SSL Certificate."""

    def setUp(self):
        super(TestCreateSSLCertificate, self).setUp()
        self.flavor_id = self.test_flavor
        self.cert_type = None
        self.domain_name = None
        self.negative_test = False

    @ddt.file_data('data_create_ssl_certificate_negative.json')
    def test_create_ssl_certificate_negative(self, test_data):
        self.negative_test = True
        self.cert_type = test_data.get('cert_type')
        self.domain_name = test_data.get('domain_name')
        flavor_id = test_data.get('flavor_id') or self.flavor_id
        project_id = self.client.project_id
        if test_data.get("missing_flavor_id", False):
            flavor_id = None

        resp = self.client.create_ssl_certificate(
            cert_type=self.cert_type,
            domain_name=self.domain_name,
            flavor_id=flavor_id,
            project_id=project_id
        )

        self.assertEqual(resp.status_code, 400)

    @ddt.file_data('data_create_ssl_certificate.json')
    def test_create_ssl_certificate_positive(self, test_data):
        if self.test_config.run_ssl_tests is False:
            self.skipTest('Create ssl certificate needs to'
                          ' be run when commanded')

        self.cert_type = test_data.get('cert_type')
        rand_string = self.generate_random_string()
        self.domain_name = rand_string + test_data.get('domain_name')
        flavor_id = test_data.get('flavor_id') or self.flavor_id
        project_id = self.client.project_id
        resp = self.client.create_ssl_certificate(
            cert_type=self.cert_type,
            domain_name=self.domain_name,
            flavor_id=flavor_id,
            project_id=project_id
        )
        self.assertEqual(resp.status_code, 202)

        resp = self.client.get_ssl_certificate(
            domain_name=self.domain_name
        )
        self.assertEqual(resp.status_code, 200)

        for cert in json.loads(resp.content):
            self.assertEqual(cert['domain_name'], self.domain_name)
            self.assertEqual(cert['flavor_id'], flavor_id)
            self.assertEqual(cert['cert_type'], self.cert_type)
            self.assertEqual(cert['project_id'], project_id)

    def tearDown(self):
        # Do not call delete cert for negative test
        if not self.negative_test:
            self.client.delete_ssl_certificate(
                cert_type=self.cert_type,
                domain_name=self.domain_name,
                flavor_id=self.flavor_id
            )
        super(TestCreateSSLCertificate, self).tearDown()
