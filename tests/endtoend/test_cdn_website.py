# coding= utf-8

# Copyright (c) 2014 Rackspace, Inc.
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
import string
import uuid

from tests.endtoend import base


class TestWebsiteCDN(base.TestBase):

    """Tests for CDN enabling a website."""

    def setUp(self):
        super(TestWebsiteCDN, self).setUp()

        def _random_string(length=12):
            return ''.join([random.choice(string.ascii_letters)
                            for _ in range(length)])

        self.stack_name = _random_string()

        self.domain_name = 'TestCDN-' + _random_string() + '.org'

        # Deploys a test website to a cloud server
        self.heat_client.create_stack(yaml_path=self.heat_config.yaml_path,
                                      stack_name=self.stack_name,
                                      domain_name=self.domain_name)
        print('Stack Name', self.stack_name)
        print('Domain Name', self.domain_name)

        self.heat_client.wait_for_stack_status(stack_name=self.stack_name)
        self.origin = self.heat_client.get_server_ip(
            stack_name=self.stack_name)
        print('Origin', self.origin)

    def test_enable_cdn(self):

        # Create a Poppy Service for the test website
        domain_list = [{"domain": self.domain_name}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
        self.service_name = str(uuid.uuid1())

        resp = self.poppy_client.create_service(
            service_name=self.service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_id=self.poppy_config.flavor)

        self.assertEqual(resp.status_code, 202)
        self.poppy_client.wait_for_service_status(
            service_name=self.service_name,
            status='DEPLOYED')

        resp = self.poppy_client.get_service(service_name=self.service_name)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']
        access_url = access_url[0]

        # Benchmark page load metrics for the CDN enabled website
        wpt_test_results = {}
        for location in self.wpt_config.test_locations:
            wpt_test_url = self.wpt_client.start_test(access_url=access_url,
                                                      test_location=location,
                                                      runs=2)
            self.wpt_client.wait_for_test_status(status='COMPLETE',
                                                 test_url=wpt_test_url)
            wpt_test_results[location] = self.wpt_client.get_test_details(
                test_url=wpt_test_url)
        print(wpt_test_results)

    def tearDown(self):
        self.heat_client.delete_stack(stack_name=self.stack_name)
        self.poppy_client.delete_service(service_name=self.service_name)
        super(TestWebsiteCDN, self).tearDown()
