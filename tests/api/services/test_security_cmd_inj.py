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

import uuid

import ddt

from nose.plugins import attrib
from tests.api import providers


@ddt.ddt
class TestCmdInjCreateService(providers.TestProviderBase):

    """Security Tests for Command Injection for Create Service."""

    def setUp(self):
        super(TestCmdInjCreateService, self).setUp()
        self.service_url = ''
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_flavor

    @attrib.attr('security')
    @ddt.file_data('data_create_service_cmdinj.json')
    def test_security_sql_inj_create_service(self, test_data):

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertEqual(resp.status_code, 400)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestCmdInjCreateService, self).tearDown()
