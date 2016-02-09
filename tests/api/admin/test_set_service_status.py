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

import ddt

from tests.api import base
from tests.api.utils.schema import admin


@ddt.ddt
class TestServiceStatus(base.TestBase):

    def setUp(self):
        super(TestServiceStatus, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')
        self.flavor_id = self.test_flavor
        self.service_urls = []

    @ddt.data((1, u'deployed'), (1, u'failed'),
              (3, u'deployed'), (3, u'failed'),
              (5, u'deployed'), (5, u'failed'))
    def test_set_services(self, services_status):
        no_of_services, status = services_status
        self.service_urls = \
            [self._service_limit_create_test_service(client=self.client)
             for _ in range(no_of_services)]

        service_ids = [url.rsplit('/')[-1:][0] for url in self.service_urls]
        project_id = self.user_project_id

        for service_id, service_url in zip(service_ids, self.service_urls):
            set_service_resp = self.operator_client.set_service_status(
                project_id=project_id,
                service_id=service_id,
                status=status)

            self.assertEqual(set_service_resp.status_code, 201)

            service_resp = self.client.get_service(service_url)
            resp_body = service_resp.json()
            resp_status = resp_body['status']
            self.assertEqual(resp_status, status)

            get_service_resp = self.operator_client.get_by_service_status(
                status=status)

            self.assertSchema(get_service_resp.json(),
                              admin.get_service_project_status)
            self.assertIn(service_id, get_service_resp.content)
            self.assertIn(project_id, get_service_resp.content)

    def tearDown(self):
        for service_url in self.service_urls:
            self.client.delete_service(location=service_url)
            if self.test_config.generate_flavors:
                self.client.delete_flavor(flavor_id=self.flavor_id)
            super(TestServiceStatus, self).tearDown()
