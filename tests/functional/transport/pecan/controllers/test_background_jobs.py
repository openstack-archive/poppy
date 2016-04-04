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
import mock

from tests.functional.transport.pecan import base


@ddt.ddt
class BackgroundJobControllerTest(base.FunctionalTest):

    def setUp(self):

        class san_cert_cnames_caller(mock.Mock):
            pass

        san_cert_cnames_caller.return_value = [
            "secure1.test_san.com",
            "secure2.test_san.com"
        ]

        background_job_controller_patcher = mock.patch(
            'poppy.provider.akamai.certificates.'
            'CertificateController.san_cert_cnames',
            new=san_cert_cnames_caller(),
        )
        background_job_controller_patcher.start()
        self.addCleanup(background_job_controller_patcher.stop)

        super(BackgroundJobControllerTest, self).setUp()

        self.project_id = str(uuid.uuid1())
        self.service_name = str(uuid.uuid1())
        self.flavor_id = str(uuid.uuid1())

    @ddt.file_data("data_post_background_jobs_bad_input.json")
    def test_post_background_job_negative(self, background_job_json):
        response = self.app.post('/v1.0/admin/provider/akamai/background_job',
                                 headers={'Content-Type': 'application/json',
                                          'X-Project-ID': self.project_id},
                                 params=json.dumps(background_job_json),
                                 expect_errors=True)

        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_post_background_jobs.json")
    def test_post_background_job_positive(self, background_job_json):
        response = self.app.post('/v1.0/admin/provider/akamai/background_job',
                                 headers={'Content-Type': 'application/json',
                                          'X-Project-ID': self.project_id},
                                 params=json.dumps(background_job_json))

        self.assertEqual(202, response.status_code)
