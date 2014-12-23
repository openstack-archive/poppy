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


@ddt.ddt
class TestAssets(base.TestBase):

    """Tests for Assets."""

    def _create_test_service(self):
        service_name = str(uuid.uuid1())

        self.domain_list = [{"domain": str(uuid.uuid1()) + '.com'}]

        self.origin_list = [{"origin": str(uuid.uuid1()) + '.com',
                             "port": 443, "ssl": False}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]

        self.client.create_service(service_name=service_name,
                                   domain_list=self.domain_list,
                                   origin_list=self.origin_list,
                                   caching_list=self.caching_list,
                                   flavor_id=self.flavor_id)
        return service_name

    def setUp(self):
        super(TestAssets, self).setUp()
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

        self.service_name = self._create_test_service()

    @attrib.attr('smoke')
    @ddt.data('True', 'true', 'TRUE', 'TRue')
    def test_purge_assets_all(self, purge_all):

        url_param = {'all': purge_all}
        resp = self.client.purge_assets(service_name=self.service_name,
                                        param=url_param)
        self.assertEqual(resp.status_code, 202)

    @attrib.attr('smoke')
    @ddt.data('mywebiste.com', 'images/maakri.jpg')
    def test_purge_assets_url(self, url):

        url_param = {'url': url}
        resp = self.client.purge_assets(service_name=self.service_name,
                                        param=url_param)
        self.assertEqual(resp.status_code, 202)

    @attrib.attr('smoke')
    def test_purge_assets_negative(self):

        url_param = {'url': 'myurl.com', 'all': True}
        resp = self.client.purge_assets(service_name=self.service_name,
                                        param=url_param)
        self.assertEqual(resp.status_code, 400)

    def tearDown(self):
        self.client.delete_service(service_name=self.service_name)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        super(TestAssets, self).tearDown()
