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

import requests

from tests.endtoend import base
from tests.endtoend.utils import config


class TestMultipleOrigin(base.TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestMultipleOrigin, cls).setUpClass()
        cls.multiorigin_config = config.MultipleOriginConfig()

        cls.default_origin = cls.multiorigin_config.default_origin
        cls.images_origin = cls.multiorigin_config.images_origin
        cls.image_path = cls.multiorigin_config.image_path

        cls.check_preconditions()

    @classmethod
    def check_preconditions(cls):
        """Ensure our environment meets our needs to ensure a valid test."""
        assert cls.default_origin != cls.images_origin
        default_root = requests.get("http://" + cls.default_origin)
        image_root = requests.get("http://" + cls.images_origin)

        assert default_root.status_code == 200
        assert image_root.status_code == 200
        assert default_root.text != image_root.text

        blank = requests.get("http://" + cls.default_origin + cls.image_path)
        image = requests.get("http://" + cls.images_origin + cls.image_path)

        assert blank.status_code == 404
        assert image.status_code == 200

    def setUp(self):
        super(TestMultipleOrigin, self).setUp()
        self.test_domain = "{0}.{1}".format(
            base.random_string('TestMultiOrigin'), self.dns_config.test_domain)
        self.service_name = base.random_string('MultiOriginService')
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
            }]
        }, {
            "origin": self.images_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "image",
                "request_url": self.image_path,
            }]
        }]

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
        self.cname_rec.append(rec)

        # Check that the CDN provider is grabbing other content from the
        # default origin, not the images origin
        self.assertSameContent(origin_url="http://" + self.default_origin,
                               cdn_url="http://" + self.test_domain)

        cdn_url = "http://{0}{1}".format(self.test_domain, self.image_path)
        origin_url = "http://{0}{1}".format(self.images_origin,
                                            self.image_path)
        response = requests.get(cdn_url)

        # On a 200, the image exists. The CDN provider fetch from the images
        # origin which is what we want.
        msg = ("Expected {0} to load the image at {1} but got {2} status code"
               .format(cdn_url, origin_url, response.status_code))
        self.assertEqual(response.status_code, 200, msg)

    def test_multiple_origin_default_last(self):
        domains = [{'domain': self.test_domain}]
        origins = [{
            "origin": self.images_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "image",
                "request_url": self.image_path,
            }]
        }, {
            "origin": self.default_origin,
            "port": 80,
            "ssl": False,
            "rules": [{
                "name": "default",
                "request_url": "/*",
            }]
        }]

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
        self.cname_rec.append(rec)

        # Everything should match the /* rule under the default origin,
        # since it's the last rule in the list
        self.assertSameContent(origin_url="http://" + self.default_origin,
                               cdn_url="http://" + self.test_domain)

        cdn_url = "http://{0}{1}".format(self.test_domain, self.image_path)
        origin_url = "http://{0}{1}".format(self.images_origin,
                                            self.image_path)
        response = requests.get(cdn_url)
        msg = ("Expected {0} to 404 on the image at {1} but got a {2} status"
               .format(cdn_url, origin_url, response.status_code))
        self.assertEqual(response.status_code, 404, msg)

    def tearDown(self):
        self.poppy_client.delete_service(location=self.service_location)
        """
        @todo(malini): Fix Bug in Delete below
        for record in self.cname_rec:
            self.dns_client.delete_record(record)
        """
        super(TestMultipleOrigin, self).tearDown()
