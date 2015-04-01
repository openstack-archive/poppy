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

import ddt
import re
import uuid

from nose.plugins import attrib

from tests.api import providers


@ddt.ddt
class TestTransportService(providers.TestProviderBase):

    """Security Tests for transport layer security vulnerablities

    The test cases check all resources related URLS in service creation
    response / service listing response/ service GET response are using
    HTTPS for transport security. Both reponse boy and all HTTP headers
    are checked. The test cases fail if HTTP is used.
    """

    def setUp(self):
        """Setup for the tests"""
        super(TestTransportService, self).setUp()
        self.service_url = ''
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_flavor

    @attrib.attr('security')
    @ddt.file_data('data_create_service.json')
    def test_check_https_for_service_creation(self, test_data):
        """Check all URLS in service creation are using HTTPS"""

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
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        # check http:// is not used in HTTP headers
        for k, v in resp.headers.iteritems():
            self.assertTrue(re.search("http://", v, re.IGNORECASE) is None)

        # check http:// is not used in response body
        self.assertTrue(re.search("http://", resp.text, re.IGNORECASE) is None)

        # list all services
        resp = self.client.list_services()
        self.assertTrue(resp.status_code == 200)

        # check http:// is not used in HTTP headers
        for k, v in resp.headers.iteritems():
            self.assertTrue(re.search("http://", v, re.IGNORECASE) is None)

        # check http:// is not used in response body
        self.assertTrue(re.search("http://", resp.text, re.IGNORECASE) is None)

        # get the service
        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        # check http:// is not used in HTTP headers
        for k, v in resp.headers.iteritems():
            self.assertTrue(re.search("http://", v, re.IGNORECASE) is None)

        # check http:// is not used in response body
        self.assertTrue(re.search("http://", resp.text, re.IGNORECASE) is None)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestTransportService, self).tearDown()
