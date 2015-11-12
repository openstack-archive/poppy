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


class TestMultipleOrigin(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestMultipleOrigin, cls).setUpClass()
        cls.multiorigin_config = config.MultipleOriginConfig()

        cls.second_origin = cls.multiorigin_config.second_origin
        cls.request_url = cls.multiorigin_config.request_url

        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        assert cls.default_origin != cls.second_origin
        default_root = cls.http_client.get("http://" + cls.default_origin)
        second_root = cls.http_client.get("http://" + cls.second_origin)

        assert default_root.status_code == 200
        assert second_root.status_code == 200

        origin_path = cls.http_client.get(
            "http://" + cls.default_origin + cls.request_url)
        second_path = cls.http_client.get(
            "http://" + cls.second_origin + cls.request_url)

        assert origin_path.status_code == 200
        assert second_path.status_code == 200
        assert origin_path.text != second_path.text

    def setUp(self):
        super(TestMultipleOrigin, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('test-multi-origin-'),
            self.dns_config.test_domain)
        self.service_name = base.random_string('E2E-MultiOrigin')
        self.cname_rec = []

    def test_multiple_origin_default_first(self):
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
        }, {
            "origin": self.second_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "Second Origin",
                "request_url": self.request_url,
            }],
            "hostheadertype": "origin"
        }]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            flavor_id=self.poppy_config.flavor)
        self.service_location = resp.headers['location']

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        # Requests to path pointed by the request_url will be fetched from the
        # second origin
        cdn_url = "http://{0}{1}".format(self.test_domain, self.request_url)
        response = self.http_client.get(cdn_url)
        self.assertIn(self.second_origin, response.text)

        # Check that the CDN provider is grabbing other content from the
        # default origin, not the second origin
        self.assertSameContent(origin_url="http://" + self.default_origin,
                               cdn_url="http://" + self.test_domain)

    def test_multiple_origin_default_last(self):
        domains = [{'domain': self.test_domain}]
        origins = [{
            "origin": self.second_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "image",
                "request_url": self.request_url,
            }],
            "hostheadertype": "origin"},
            {"origin": self.default_origin,
             "port": 80,
             "ssl": False,
             "rules": [{
                 "name": "default",
                 "request_url": "/*",
             }],
             "hostheadertype": "origin"}
        ]

        self.setup_service(
            service_name=self.service_name,
            domain_list=domains,
            origin_list=origins,
            caching_list=[],
            flavor_id=self.poppy_config.flavor)

        resp = self.poppy_client.get_service(location=self.service_location)
        links = resp.json()['links']
        access_url = [link['href'] for link in links if
                      link['rel'] == 'access_url']

        rec = self.setup_cname(self.test_domain, access_url[0])
        if rec:
            self.cname_rec.append(rec[0])

        # Everything should match the /* rule under the default origin,
        # since it's the last rule in the list
        self.assertSameContent(origin_url="http://" + self.default_origin,
                               cdn_url="http://" + self.test_domain)

        # More strict rules should come after less strict rules.
        # Hence requests to the path pointed by request_url will also be
        # routed to the default origin, based on how we setup the origin rules.
        cdn_url = "http://{0}{1}".format(self.test_domain, self.request_url)
        response = self.http_client.get(cdn_url)
        self.assertIn(self.default_origin, response.text)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        super(TestMultipleOrigin, self).tearDown()
