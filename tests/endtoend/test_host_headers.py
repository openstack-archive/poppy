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

from tests.endtoend import base
from tests.endtoend.utils import config


class TestHostHeaders(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestHostHeaders, cls).setUpClass()

        cls.host_header_config = config.HostHeaderConfig()

        cls.default_origin = cls.host_header_config.origin
        cls.test_endpoint = cls.host_header_config.endpoint
        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        origin = cls.http_client.get(
            "http://" + cls.default_origin + cls.test_endpoint)

        assert origin.status_code == 200

    def setUp(self):
        super(TestHostHeaders, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-origin-hostheader'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('OriginHostHeaderService')
        self.cname_rec = []

    def test_origin_host_header(self):
        domains = [{'domain': self.test_domain}]
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
            "hostheadertype": "origin"
        }]
        caching = [
            {"name": "default",
             "ttl": 3600,
             "rules": [{"name": "default", "request_url": "/*"}]}]
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain
        resp = self.http_client.get(url=cdn_url + self.test_endpoint)
        self.assertIn(self.default_origin, resp.content)

    def test_custom_host_header(self):
        domains = [{'domain': self.test_domain}]
        host_header_value = 'llama-llama-red-pajama.com'
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }],
            "hostheadertype": "custom",
            "hostheadervalue": host_header_value
        }]
        caching = [
            {"name": "default",
             "ttl": 3600,
             "rules": [{"name": "default", "request_url": "/*"}]}]
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain
        url = cdn_url + self.test_endpoint
        resp = self.http_client.get(url=url)
        self.assertIn(host_header_value, resp.content)

    def test_default_host_header(self):
        domains = [{'domain': self.test_domain}]
        origins = [{
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }]
        }]
        caching = [
            {"name": "default",
             "ttl": 3600,
             "rules": [{"name": "default", "request_url": "/*"}]}]
        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=caching,
            flavor_id=self.poppy_config.flavor)

        self.service_location = resp.headers['location']
        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        cdn_url = 'http://' + self.test_domain
        url = cdn_url + self.test_endpoint
        resp = self.http_client.get(url=url)
        self.assertIn(self.test_domain, resp.content)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestHostHeaders, self).tearDown()
