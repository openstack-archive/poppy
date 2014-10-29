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

import uuid

import ddt

from tests.api import base
from tests.api import providers
from tests.api.utils.schema import services


@ddt.ddt
class TestCreateService(providers.TestProviderBase):

    """Tests for Create Service."""

    def setUp(self):
        super(TestCreateService, self).setUp()
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

        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertSchema(body, services.get_service)

        self.assertEqual(body['domains'], domain_list)
        self.assertEqual(body['origins'], origin_list)

        # TODO(malini): uncomment below after caching list is implemented.
        # self.assertEqual(body['caching_list'], caching_list)

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
        super(TestCreateService, self).tearDown()


@ddt.ddt
class TestListServices(base.TestBase):
    """Tests for List Services."""

    def _create_test_service(self):
        service_name = str(uuid.uuid1())

        self.domain_list = [{"domain": "mywebsite.com"},
                            {"domain": "blog.mywebsite.com"}]

        self.origin_list = [{"origin": "mywebsite.com",
                             "port": 443, "ssl": False}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]

        self.client.create_service(service_name=service_name,
                                   domain_list=self.domain_list,
                                   origin_list=self.origin_list,
                                   caching_list=self.caching_list,
                                   flavorRef='standard')
        return service_name

    def setUp(self):
        super(TestListServices, self).setUp()
        self.service_list = []

    def test_list_single_service(self):
        self.service_list.append(self._create_test_service())
        resp = self.client.list_services()
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertSchema(body, services.list_services)

    def test_list_services_no_service(self):
        self.skipTest('Non deterministic - Replace this with an unit test?')
        resp = self.client.list_services()
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(body['services'], [])
        self.assertEqual(body['links'], [])

    @ddt.data(1, 5, 10)
    def test_list_services_valid_limit(self, limit):
        self.service_list = [self._create_test_service() for _ in range(limit)]
        url_param = {'limit': limit}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(len(body['services']), limit)
        self.assertSchema(body, services.list_services)

    def test_list_services_multiple_page(self):
        self.service_list = [self._create_test_service() for _ in range(25)]
        resp = self.client.list_services()
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        # TODO(malini): remove hard coded value with configurable value
        self.assertEqual(len(body['services']), 10)
        self.assertSchema(body, services.list_services)

    # TODO(malini):
    # Uncomment after bug fix - https://bugs.launchpad.net/poppy/+bug/1384271
    # @ddt.data(-1, -10000000000, 0, 10000000, 'invalid', '学校', '')
    @ddt.data(-1, -10000000000, 0, 10000000, 'invalid', '')
    def test_list_services_invalid_limits(self, limit):
        url_param = {'limit': limit}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 400)

    @ddt.data(-1, -10000000000, 0, 10000000, 'invalid', '学校', '')
    def test_list_services_various_markers(self, marker):
        url_param = {'marker': marker}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

    def test_list_services_invalid_param(self):
        url_param = {'yummy': 123}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        for service in self.service_list:
            self.client.delete_service(service_name=service)
        super(TestListServices, self).tearDown()


@ddt.ddt
class TestServiceActions(base.TestBase):

    """Tests for PATCH, GET & DELETE Services."""

    def setUp(self):
        super(TestServiceActions, self).setUp()
        self.service_name = str(uuid.uuid1())
        self.domain_list = [{"domain": "mywebsite.com"},
                            {"domain": "blog.mywebsite.com"}]

        self.origin_list = [{"origin": "mywebsite.com",
                             "port": 443, "ssl": False}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]

        self.client.create_service(service_name=self.service_name,
                                   domain_list=self.domain_list,
                                   origin_list=self.origin_list,
                                   caching_list=self.caching_list,
                                   flavorRef='standard')

    def test_get_service(self):

        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertSchema(body, services.get_service)
        self.assertEqual(body['domains'], self.domain_list)
        self.assertEqual(body['origins'], self.origin_list)
        # TODO(malini): uncomment below after caching list is implemented.
        # self.assertEqual(body['caching_list'], self.caching_list)
        # self.assertEqual(body['status'], 'create_in_progress')
        self.assertEqual(body['status'], 'deployed')

    def test_get_non_existing_service(self):

        resp = self.client.get_service(service_name='this_cant_be_true')
        self.assertEqual(resp.status_code, 404)

    def test_get_failed_service(self):
        # TODO(malini): Add test to verify that failed service will return
        # status 'failed' on get_service with error message from the provider.
        # Placeholder till we figure out how to create provider side failure.
        pass

    def test_delete_service(self):
        resp = self.client.delete_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 202)

        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        # self.assertEqual(body['status'], 'delete_in_progress')
        self.assertEqual(body['status'], 'deployed')

        # TODO(malini): find a better solution
        # As is, the servvice is still available in the DB till deleted from
        # the provider. The test should be able to handle this with
        # exponential sleep or whatever(!).
        # time.sleep(20)
        # resp = self.client.get_service(service_name=self.service_name)
        # self.assertEqual(resp.status_code, 404)

    def test_delete_non_existing_service(self):
        resp = self.client.delete_service(service_name='this_cant_be_true')
        self.assertEqual(resp.status_code, 404)

    def test_delete_failed_service(self):
        # TODO(malini): Add test to verify that a failed service can be
        # deleted.
        # Placeholder till we figure out how to create provider side failure.
        pass

    def tearDown(self):
        self.client.delete_service(service_name=self.service_name)
        super(TestServiceActions, self).tearDown()
