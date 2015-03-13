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
from tests.api import providers


@ddt.ddt
class TestPatchService(providers.TestProviderBase):

    """Security Tests for possible vulnerabilities
        for patching calls."""

    def setUp(self):
        """
        Setup for the tests
        """
        super(TestPatchService, self).setUp()
        self.domain_list = [{"domain": "mywebsite%s.com" % str(uuid.uuid1())}]
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
        self.MAX_ATTEMPTS = 30

        if self.test_config.generate_flavors:
            # create the flavor
            self.flavor_id = str(uuid.uuid1())
            self.client.create_flavor(flavor_id=self.flavor_id,
                                      provider_list=[{
                                          "provider": "fastly",
                                          "links": [{"href": "www.fastly.com",
                                                     "rel": "provider_url"}]}])
        #create a service
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']

    def reset_defaults(self):
        """
        Reset domain_list, origin_list, caching_list, service_name
        and flavor_id to its default value.
        """
        self.domain_list = [{"domain": "mywebsite%s.com" % str(uuid.uuid1())}]
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

    @attrib.attr('security')
    def test_patch_service_multiple_domains_dos(self):
        """
        Create a service and immediately patch the service with large
        number of domains.
        """
        for k in range(1, 100):
            #create a service
            self.domain_list = [{"domain":
                                 "mywebsite%s.com" % str(uuid.uuid1())}]
            resp = self.client.create_service(service_name=self.service_name,
                                              domain_list=self.domain_list,
                                              origin_list=self.origin_list,
                                              caching_list=self.caching_list,
                                              flavor_id=self.flavor_id)
            if 'location' in resp.headers:
                self.service_url = resp.headers['location']

            domain_name = "replacemereplaceme%s.com" % str(uuid.uuid1())
            test_data = []
            for j in range(1, 60):
                test_data.append(
                    {"op": "add",
                     "path": "/domains/-",
                     "value": {"domain": "%s%s" % (j, domain_name)}})

            resp = self.client.patch_service(location=self.service_url,
                                             request_body=test_data)
            if resp.status_code == 400:
                continue
            resp = self.client.get_service(location=self.service_url)
            self.assertTrue(resp.status_code < 500)

    @attrib.attr('security')
    def test_patch_service_add_delete_dos(self):
        """
        Create a service and immediately patch the service with large
        number of domains.
        """
        for k in range(1, 100):
            #create a service
            self.domain_list = [{"domain":
                                 "mywebsite%s.com" % str(uuid.uuid1())}]
            resp = self.client.create_service(service_name=self.service_name,
                                              domain_list=self.domain_list,
                                              origin_list=self.origin_list,
                                              caching_list=self.caching_list,
                                              flavor_id=self.flavor_id)
            if 'location' in resp.headers:
                self.service_url = resp.headers['location']

            domain_name = "replacemereplaceme%s.com" % str(uuid.uuid1())
            test_data = []
            for j in range(1, 30):
                test_data.append(
                    {"op": "add",
                     "path": "/domains/-",
                     "value": {"domain": "%s%s" % (j, domain_name)}})
                test_data.append(
                    {"op": "remove",
                     "path": "/domains/%s" % j})

            resp = self.client.patch_service(location=self.service_url,
                                             request_body=test_data)
            if resp.status_code == 400:
                continue
            resp = self.client.get_service(location=self.service_url)
            self.assertTrue(resp.status_code < 500)

    @attrib.attr('security')
    def test_patch_service_delete_domains_dos(self):
        """
        Create a service and immediately patch the service with large
        number of domains.
        """
        for k in range(1, 100):
            #create a service
            self.domain_list = [{"domain":
                                 "mywebsite%s.com" % str(uuid.uuid1())}]
            resp = self.client.create_service(service_name=self.service_name,
                                              domain_list=self.domain_list,
                                              origin_list=self.origin_list,
                                              caching_list=self.caching_list,
                                              flavor_id=self.flavor_id)
            if 'location' in resp.headers:
                self.service_url = resp.headers['location']

            # domain_name = "replacemereplaceme%s.com" % str(uuid.uuid1())
            test_data = []
            for j in range(0, 60):
                test_data.append(
                    {"op": "remove",
                     "path": "/domains/%s" % (-1 * j)})

            resp = self.client.patch_service(location=self.service_url,
                                             request_body=test_data)
            if resp.status_code == 400:
                continue
            resp = self.client.get_service(location=self.service_url)
            self.assertTrue(resp.status_code < 500)

    @attrib.attr('security')
    def test_patch_service_adding_origins_dos(self):
        """
        Create a service and add lots of origins.
        """
        for k in range(1, 100):
            #create a service
            self.domain_list = [{"domain":
                                 "mywebsite%s.com" % str(uuid.uuid1())}]
            resp = self.client.create_service(service_name=self.service_name,
                                              domain_list=self.domain_list,
                                              origin_list=self.origin_list,
                                              caching_list=self.caching_list,
                                              flavor_id=self.flavor_id)
            if 'location' in resp.headers:
                self.service_url = resp.headers['location']

            test_data = []
            for j in range(1, 60):
                test_data.append(
                    {"op": "add",
                     "path": "/origins/%s" % j,
                     "value": {"origin": "1.2.3.4", "port": 80, "ssl": "false",
                               "rules": [{"name": "origin",
                                          "request_url": "/origin.htm"}]}})

            resp = self.client.patch_service(location=self.service_url,
                                             request_body=test_data)
            if resp.status_code == 400:
                continue
            resp = self.client.get_service(location=self.service_url)
            self.assertTrue(resp.status_code < 500)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestPatchService, self).tearDown()
