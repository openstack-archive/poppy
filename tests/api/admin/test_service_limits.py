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
import uuid

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

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

    def _alt_create_test_service(self, resp_code=False):
        service_name = str(uuid.uuid1())

        domain_list = [{"domain": self.generate_random_string(
            prefix='www.api-test-domain') + '.com'}]

        origin_list = [{"origin": self.generate_random_string(
            prefix='api-test-origin') + '.com', "port": 80, "ssl": False,
            "hostheadertype": "custom", "hostheadervalue":
            "www.customweb.com"}]

        self.log_delivery = {"enabled": False}

        resp = self.alt_user_client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=self.caching_list,
            flavor_id=self.flavor_id,
            log_delivery=self.log_delivery)

        if resp_code:
            return resp

        self.assertEqual(resp.status_code, 202)
        service_url = resp.headers["location"]

        return service_url

    def _alt_delete_services(self):
        services = self.alt_user_client.list_services()
        del_service_urls = []

        services_content = json.loads(services.content)
        total_services = services_content['services']
        for service in total_services:
            for link in service['links']:
                if link['rel'] == 'self':
                    del_service_urls.append(link['href'])

        for service in del_service_urls:
            self.alt_user_client.delete_service(location=service)
            self.alt_user_client.wait_for_service_delete(
                location=service,
                retry_timeout=self.test_config.status_check_retry_timeout,
                retry_interval=self.test_config.status_check_retry_interval)

    def test_service_limit_parameters(self):
        invalid_limit = -5
        valid_limit = 1000

        # no limits, should result in a 400.
        resp = self.operator_client.admin_service_limit(
            project_id=self.user_project_id)
        self.assertEqual(resp.status_code, 400)

        # invalid limits, should result in a 400.
        resp = self.operator_client.admin_service_limit(
            project_id=self.user_project_id, limit=invalid_limit)
        self.assertEqual(resp.status_code, 400)

        # valid limits, results in a 201
        resp = self.operator_client.admin_service_limit(
            project_id=self.user_project_id, limit=valid_limit)
        self.assertEqual(resp.status_code, 201)

    @ddt.data(1, 3, 5)
    def test_check_imposed_limit_on_services(self, limit):

        self._alt_delete_services()

        resp = self.operator_client.admin_service_limit(
            project_id=self.alt_user_client.project_id,
            limit=limit)

        self.assertEqual(resp.status_code, 201)

        self.service_list = [self._alt_create_test_service()
                             for _ in range(limit)]

        resp = self._alt_create_test_service(resp_code=True)
        self.assertEqual(resp.status_code, 403)

        resp = self.operator_client.get_admin_service_limit(
            project_id=self.alt_user_client.project_id
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['limit'], limit)

        for service in self.service_list:
            self.alt_user_client.delete_service(location=service)
            self.alt_user_client.wait_for_service_delete(
                location=service,
                retry_timeout=self.test_config.status_check_retry_timeout,
                retry_interval=self.test_config.status_check_retry_interval)
