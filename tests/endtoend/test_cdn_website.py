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
        self.stack_name = str(uuid.uuid1())

        self.domain_name = ''.join([random.choice(string.ascii_letters)
                                    for _ in range(12)]) + '.in'

        self.heat_client.create_stack(stack_name=self.stack_name,
                                      domain_name=self.domain_name)

        self.heat_client.wait_for_stack_status(stack_name=self.stack_name)
        self.origin = self.heat_client.get_server_ip(
            stack_name=self.stack_name)

    def test_enable_cdn(self, test_data):

        domain_list = [{"domain": self.domain_name}]
        origin_list = [{"origin": self.origin,
                        "port": 80,
                        "ssl": False}]
        caching_list = []
        flavor = 'standard'
        service_name = str(uuid.uuid1())

        resp = self.poppy_client.create_service(
            service_name=service_name,
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list,
            flavor_ref=flavor)

        self.assertEqual(resp.status_code, 202)
        self.poppy_client.wait_for_service_status(service_name=service_name,
                                                  status='DEPLOYED')

    def tearDown(self):
        self.heat_client.delete_stack(stack_name=self.stack_name)
        super(TestWebsiteCDN, self).tearDown()
