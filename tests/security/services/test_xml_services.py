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
import re


@ddt.ddt
class TestXMLService(providers.TestProviderBase):

    """Security Tests for any XML related  Service vulnerablities"""

    def setUp(self):
        """
        Setup for the tests
        """
        super(TestXMLService, self).setUp()
        self.domain_list = [{"domain": "mywebsite.com"}]
        self.origin_list = [{"origin": "mywebsite1.com",
                             "port": 443,
                             "ssl": False}]
        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home",
                              "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
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
        self.domain_list = [{"domain": "mywebsite.com"}]
        self.origin_list = [{"origin": "mywebsite1.com",
                             "port": 443,
                             "ssl": False}]
        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home",
                              "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_config.default_flavor

    @attrib.attr('security')
    def test_xml_bomb_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a service using XML bomb.
        """
        # replace content type with application/xml
        headers = {"X-Auth-Token": self.client.auth_token,
                   "X-Project-Id": self.client.project_id,
                   "Content-Type": "application/xml"}
        attack_string = """
        <?xml version="1.0"?>
        <!DOCTYPE lolz [
<!ENTITY lol "lol">
<!ELEMENT lolz (#PCDATA)>
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
<!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
<!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
<!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
<!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
<!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
 ]>
<lolz>&lol9;</lolz>
        """
        kwargs = {"headers": headers, "data": attack_string}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        # delete the service
        self.assertTrue(resp.status_code == 400)
        match = re.search("Invalid JSON string", resp.text)
        self.assertTrue(match is not None)

    def tearDown(self):
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestXMLService, self).tearDown()

