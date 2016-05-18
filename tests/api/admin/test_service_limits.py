# coding= utf-8

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
class TestServiceLimits(base.TestBase):

    def setUp(self):
        super(TestServiceLimits, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        self.flavor_id = self.test_flavor
        self.service_list = []

    @ddt.data(-1, -10000000000, 'invalid', '学校', '', None)
    def test_service_limit_parameters_invalid(self, limit):

        resp = self.operator_client.admin_service_limit(
            project_id=self.user_project_id,
            limit=limit)
        self.assertEqual(resp.status_code, 400)

    @ddt.data(1, 3, 5)
    def test_check_imposed_limit_on_services(self, limit):

        resp = self.service_limit_user_client.list_services()

        body = resp.json()

        if body["services"] != [] or body["links"] != []:
            self.fail(
                "Testing services limits expects an account that "
                "doesn't have existing services. Found services: "
                "{0}".format(body["services"])
            )

        resp = self.operator_client.admin_service_limit(
            project_id=self.service_limit_user_client.project_id,
            limit=limit)

        self.assertEqual(resp.status_code, 201)

        self.service_list = [self._service_limit_create_test_service(
            client=self.service_limit_user_client)
            for _ in range(limit)]

        resp = self._service_limit_create_test_service(
            client=self.service_limit_user_client,
            resp_code=True)
        self.assertEqual(resp.status_code, 403)

        resp = self.operator_client.get_admin_service_limit(
            project_id=self.service_limit_user_client.project_id
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['limit'], limit)

    def tearDown(self):
        for service in self.service_list:
            self.service_limit_user_client.delete_service(location=service)
            self.service_limit_user_client.wait_for_service_delete(
                location=service,
                retry_timeout=self.test_config.status_check_retry_timeout,
                retry_interval=self.test_config.status_check_retry_interval)
