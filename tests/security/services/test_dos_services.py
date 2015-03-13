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
import gzip
import StringIO
from nose.plugins import attrib
from tests.api import providers


@ddt.ddt
class TestDOSCreateService(providers.TestProviderBase):

    """Security Tests for Denail of Service vulnerablities
        for creating Service."""

    def setUp(self):
        """
        Setup for the tests
        """
        super(TestDOSCreateService, self).setUp()
        self.domain_list = [{"domain": "mywebsite%s.com" % uuid.uuid1()}]
        self.origin_list = [{"origin": "mywebsite1.com",
                             "port": 443,
                             "ssl": False}]
        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home",
                              "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.restrictions_list = [
            {
                u"name": u"website only",
                u"rules": [
                    {
                        u"name": "mywebsite.com",
                        u"referrer": "mywebsite.com"
                    }
                ]
            }
        ]
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

    def create_invalid_json(self, length):
        """
        Create invalid_json like [[[[[[[[[[[[[test]]]]]]]]]]]]]
        """
        str = ""
        str += "[" * length
        str += "\"test\""
        str += "]" * length
        return str

    def create_malicious_json(self, length):
        """
        Create malicious json like {{{{t:{{{{{}}}}}}}}}
        """
        str = "{"
        for k in range(0, length):
            str += "\"t%s\":{" % k
        str += "\"t\":\"t\""
        for k in range(0, length):
            str += "}"
        str += "}"
        return str

    def data_zip(self, data):
        """
        zip the data using gzip format
        """
        stringio = StringIO.StringIO()
        gzip_file = gzip.GzipFile(fileobj=stringio, mode='wb')
        gzip_file.write(data)
        gzip_file.close()
        return stringio.getvalue()

    def check_one_request(self):
        """
        Check the response of one request to see whether one request can
        kill the application.
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

        # delete the service
        self.assertTrue(resp.status_code < 503)

        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

    @attrib.attr('security')
    def test_invalid_json_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a big invalid json blob.
        """
        # create a payload with invalid json blob
        attack_string = self.create_invalid_json(2500)
        kwargs = {"data": attack_string}
        print kwargs
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_malicious_json_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a big malicious json blob.
        """
        # create a payload with malicous json blob
        attack_string = self.create_malicious_json(900)
        headers = {"X-Auth-Token": self.client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers, "data": attack_string}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_malicious_json_utf_8_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a big malicious json blob with utf-8 encoding.
        """
        # create a payload with malicous json blob
        attack_string = self.create_malicious_json(800)
        headers = {"X-Auth-Token": self.client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers, "data": attack_string.encode("utf-8")}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_create_service_with_big_project_id(self):
        """
        Check whether it is possible to kill the application by
        creating service with big X-Project-Id header.
        """
        failed_count = 0
        for k in range(2500, 8000, 500):
            self.reset_defaults()
            headers = {"X-Auth-Token": self.client.auth_token,
                       "X-Project-Id": "1"*k,
                       "Content-Type": "application/json"}
            kwargs = {"headers": headers}
            self.service_name = str(uuid.uuid1())
            resp = self.client.create_service(service_name=self.service_name,
                                              domain_list=self.domain_list,
                                              origin_list=self.origin_list,
                                              caching_list=self.caching_list,
                                              flavor_id=self.flavor_id,
                                              requestslib_kwargs=kwargs)
            if 'location' in resp.headers:
                self.service_url = resp.headers['location']
            else:
                self.service_url = ''

            #self.assertTrue(resp.status_code < 503)
            if (resp.status_code == 503):
                failed_count += 1
            resp = self.client.list_services(requestslib_kwargs=kwargs)
            if (resp.status_code == 503):
                failed_count += 1
            self.assertTrue(failed_count <= 3)
            #self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_malicious_json_utf_16_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a big malicious json blob with utf-16 encoding.
        """
        # create a payload with malicous json blob
        attack_string = self.create_malicious_json(400)
        headers = {"X-Auth-Token": self.client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers, "data": attack_string.encode("utf-16")}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_malicious_json_gzip_create_service(self):
        """
        Check whether it is possible to kill the application by
        creating a big malicious json blob with gzip.
        """
        # create a payload with malicious json blob
        attack_string = self.create_malicious_json(2500)
        headers = {"X-Auth-Token": self.client.auth_token,
                   "X-Project-Id": self.client.project_id,
                   "Content-Encoding": "gzip"}
        kwargs = {"headers": headers, "data": self.data_zip(attack_string)}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_dos_create_service_domain_list(self):
        """
        Check whether it is possible to kill the application by
        creating a service with huge list of domains.
        """
        # create a huge list of domain
        self.reset_defaults()
        for k in range(1, 30000):
            self.domain_list.append({"domain": "w.t%s.com" % k})

        # send MAX_ATTEMPTS requests
        for k in range(1, self.MAX_ATTEMPTS):
            self.service_name = str(uuid.uuid1())
            self.check_one_request()

    @attrib.attr('security')
    def test_dos_create_service_origin_list(self):
        """
        Check whether it is possible to kill the application by
        creating a service with huge list of origins.
        """
        # create a huge list of domain
        self.reset_defaults()
        for k in range(1, 9000):
            self.origin_list.append({"origin": "m%s.com" % k,
                                     "port": 443,
                                     "ssl": False,
                                     "rules": [{"request_url": "/i.htm",
                                                "name": "i"}]})

        # send MAX_ATTEMPTS requests
        for k in range(1, self.MAX_ATTEMPTS):
            self.service_name = str(uuid.uuid1())
            self.check_one_request()

    @attrib.attr('security')
    def test_dos_create_service_caching_list(self):
        """
        Check whether it is possible to kill the application by
        creating a service with huge list of caching.
        """
        # create a huge list of domain
        self.reset_defaults()
        for k in range(1, 16000):
            self.caching_list.append({"name": "d%s" % k, "ttl": 3600,
                                      "rules": [{"request_url": "/i.htm",
                                                "name": "i"}]})

        # send MAX_ATTEMPTS requests
        for k in range(1, self.MAX_ATTEMPTS):
            self.service_name = str(uuid.uuid1())
            self.check_one_request()

    @attrib.attr('security')
    def test_dos_create_service_caching_list_rules(self):
        """
        Check whether it is possible to kill the application by
        creating a service with huge list rules within caching list.
        """
        # create a huge list of domain
        self.reset_defaults()
        for k in range(1, 15000):
            self.caching_list[1]["rules"].append(
                {"name": "i%s" % k,
                 "request_url": "/index.htm"})

        # send MAX_ATTEMPTS requests
        for k in range(1, self.MAX_ATTEMPTS):
            self.service_name = str(uuid.uuid1())
            self.check_one_request()

    @attrib.attr('security')
    def test_dos_list_service_huge_limit(self):
        """
        Check whether it is possible to kill the application by
        listing all services with a huge limit
        """
        # create a huge list of domain
        attack_string = "1" * 3500
        params = {"limit": attack_string, "marker": attack_string}
        resp = self.client.list_services(param=params)
        self.assertTrue(resp.status_code < 503)

    @attrib.attr('security')
    def test_dos_list_service_huge_junk(self):
        """
        Check whether it is possible to kill the application by
        listing all services with a huge junk parameter
        """
        # create a huge list of domain
        attack_string = "1" * 3500
        params = {"junk": attack_string}
        resp = self.client.list_services(param=params)
        self.assertTrue(resp.status_code < 503)

    def tearDown(self):
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestDOSCreateService, self).tearDown()
