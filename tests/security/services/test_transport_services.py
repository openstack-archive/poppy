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
import re
from nose.plugins import attrib
from tests.api import providers


@ddt.ddt
class TestTransportService(providers.TestProviderBase):

    """Security Tests for transport layer security vulnerablities
        for service calls."""

    def setUp(self):
        """
        Setup for the tests
        """
        super(TestTransportService, self).setUp()
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
        self.MAX_ATTEMPTS = 30

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
        Create one service and check whether it has been
        sucessfully created.
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

        self.assertTrue(resp.status_code == 202)

    @attrib.attr('security')
    def test_transport_check_https(self):
        """
        Check whether https is used for all links returned from get_service
        calls. If https is not used in any link, the test fails.
        """
        self.reset_defaults()
        self.service_name = str(uuid.uuid1())
        # create one service
        self.check_one_request()
        resp = self.client.list_services()
        # make sure that http:// is not used anywhere
        self.assertTrue(re.search("http://", resp.text) is None)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestTransportService, self).tearDown()
