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

import uuid

import ddt

from tests.api import providers
# from tests.api.utils.schema import response - Uncomment after get_service API


@ddt.ddt
class TestServices(providers.TestProviderBase):

    """Tests for Services."""

    def setUp(self):
        super(TestServices, self).setUp()
        self.service_name = str(uuid.uuid1())

    @ddt.file_data('data_create_service.json')
    def test_create_service(self, test_data):

        domain_list = test_data['domain_list']
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor = test_data['flavorRef']

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavorRef=flavor)
        self.assertEqual(resp.status_code, 202)

        # TODO(malini): uncomment after get_service endpoint is complete.
        '''
        # Get on Created Service
        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertSchema(body, response.create_service)

        self.assertEqual(body['domains'], domain_list)
        self.assertEqual(body['origins'], origin_list)
        self.assertEqual(body['caching_list'], caching_list)
        '''

        # Verify the service is updated at all Providers for the flavor
        if self.test_config.provider_validation:
            service_details = (
                self.getServiceFromFlavor(flavor, self.service_name))
            provider_list = self.config.flavor[flavor]

            # Verify that the service stored in each provider (that is part of
            # the flavor) is what Poppy sent them.
            for provider in provider_list:
                self.assertEqual(
                    sorted(service_details[provider]['domain_list']),
                    sorted(domain_list),
                    msg='Domain Lists Not Correct for {0} service name {1}'.
                        format(provider, self.service_name))
                self.assertEqual(
                    sorted(service_details[provider]['origin_list']),
                    sorted(origin_list),
                    msg='Origin List Not Correct for {0} service name {1}'.
                        format(provider, self.service_name))
                self.assertEqual(
                    sorted(service_details[provider]['caching_list']),
                    sorted(caching_list),
                    msg='Caching List Not Correct for {0} service name {1}'.
                        format(provider, self.service_name))

    @ddt.file_data('data_create_service_negative.json')
    def test_create_service_negative(self, test_data):

        service_name = test_data['service_name']
        domain_list = test_data['domain_list']
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor = test_data['flavorRef']

        resp = self.client.create_service(service_name=service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavorRef=flavor)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_service(service_name=self.service_name)
        super(TestServices, self).tearDown()
