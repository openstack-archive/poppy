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
from nose.plugins import attrib
from tests.api import base
from tests.api import providers


@ddt.ddt
class TestSecuritySQLInjCreateService(providers.TestProviderBase):

    """Security Tests for SQL Injection  vulnerabilities
        for creating Service."""

    def setUp(self):
        """
        Setup for the tests
        """
        super(TestSecuritySQLInjCreateService, self).setUp()
        self.domain_list = [{"domain": "mywebsite%s.com" % uuid.uuid1()}]
        self.origin_list = [{"origin": "mywebsite1.com",
                             "port": 443,
                             "ssl": False}]
        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home",
                              "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.service_url = ''
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_config.default_flavor

        if self.test_config.generate_flavors:
            # create the flavor
            self.flavor_id = str(uuid.uuid1())
            self.client.create_flavor(flavor_id=self.flavor_id,
                                      provider_list=[{
                                          "provider": "fastly",
                                          "links": [{"href": "www.fastly.com",
                                                     "rel": "provider_url"}]}])

    def reset_defaults(self):
        """
        Reset domain_list, origin_list, caching_list, service_name
        and flavor_id to its default value.
        """
        self.domain_list = [{"domain": "mywebsite%s.com" % uuid.uuid1()}]
        self.origin_list = [{"origin": "mywebsite1.com",
                             "port": 443,
                             "ssl": False}]
        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home",
                              "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.service_url = ''
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_config.default_flavor

    def check_one_request(self):
        """
        Check the response of one request to see whether the application
        is vulnerable to sql injection.
        """
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        # todo: change this to something reasonable once the environment is
        # stable
        # see Flavor SQL Inj script
        #self.assertEqual(resp.status_code, 202)
        self.assertTrue(resp.status_code > 200)
        # delete the service
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

    @attrib.attr('security')
    @ddt.file_data('data_sql_inj.json')
    def test_security_sql_inj_create_service(self, test_data):
        """
        Check whether the application is vulnerable to sql injection.
        """
        self.reset_defaults()
        #check domain list values
        for k in test_data:
            for key in self.domain_list[0]:
                self.service_name = str(uuid.uuid1())
                self.domain_list[0][key] = test_data['sql_inj_string']
                self.check_one_request()
                self.reset_defaults()
        #check origin list values
        for k in test_data:
            for key in self.origin_list[0]:
                self.service_name = str(uuid.uuid1())
                self.origin_list[0][key] = test_data['sql_inj_string']
                self.check_one_request()
                self.reset_defaults()
        #check the caching list values
        for k in test_data:
            for key in self.caching_list[1]:
                self.service_name = str(uuid.uuid1())
                # to do. This is currently tied with existing examples.
                if isinstance(self.caching_list[1][key], (list)):
                    for the_key in self.caching_list[1][key][0]:
                        self.caching_list[1][key][0][the_key] = test_data
                        ['sql_inj_string']
                        self.check_one_request()
                        self.reset_defaults()
                else:
                    self.caching_list[1][key] = test_data['sql_inj_string']
                    self.check_one_request()
                    self.reset_defaults()
        #check the service name
        for k in test_data:
            self.service_name = test_data['sql_inj_string']
            self.check_one_request()
            self.reset_defaults()

        #check the flavor_id
        for k in test_data:
            self.flavor_id = test_data['sql_inj_string']
            self.check_one_request()
            self.reset_defaults()

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestSecuritySQLInjCreateService, self).tearDown()


@ddt.ddt
class TestSecuritySQLInjListServices(base.TestBase):
    """Tests for List Services."""

    def _create_test_service(self):
        service_name = str(uuid.uuid1())

        self.domain_list = [{"domain": str(uuid.uuid1()) + '.com'}]

        self.origin_list = [{"origin": str(uuid.uuid1()) + '.com',
                             "port": 443, "ssl": False}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]

        resp = self.client.create_service(service_name=service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''
        return service_name

    def setUp(self):
        super(TestSecuritySQLInjListServices, self).setUp()
        self.service_list = []
        if self.test_config.generate_flavors:
            self.flavor_id = str(uuid.uuid1())
            self.client.create_flavor(
                flavor_id=self.flavor_id,
                provider_list=[{"provider": "fastly",
                                "links": [{"href": "www.fastly.com",
                                           "rel": "provider_url"}]}])
        else:
            self.flavor_id = self.test_config.default_flavor

    @attrib.attr('security')
    @ddt.file_data('data_sql_inj.json')
    def test_list_services_sql_inj_limits(self, test_data):
        """
        Test whether is possible to inject sql in limit parameter
        """
        url_param = {'limit': test_data['sql_inj_string']}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 400)

    @attrib.attr('security')
    @ddt.file_data('data_sql_inj.json')
    def test_list_services_sql_inj_marker(self, test_data):
        url_param = {'marker': test_data['sql_inj_string']}
        resp = self.client.list_services(param=url_param)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        for service in self.service_list:
            if self.service_url != '':
                self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestSecuritySQLInjListServices, self).tearDown()
