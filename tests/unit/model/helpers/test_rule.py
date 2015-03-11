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

from poppy.model.helpers import rule
from tests.unit import base


@ddt.ddt
class TestRule(base.TestCase):

    def test_rule(self):

        name = 'name'
        http_host = 'www.mywebsite.com'
        client_ip = '192.168.1.1'
        http_method = 'POST'
        request_url = '/index.html'
        geography = 'USA'

        myrule = rule.Rule(name)

        # test all properties
        # name
        self.assertEqual(myrule.name, name)
        self.assertRaises(AttributeError, setattr, myrule, 'name', name)

        # http_host
        myrule.http_host = http_host
        self.assertEqual(myrule.http_host, http_host)

        # client_ip
        myrule.client_ip = client_ip
        self.assertEqual(myrule.client_ip, client_ip)

        # http_method
        myrule.http_method = http_method
        self.assertEqual(myrule.http_method, http_method)

        # request_url
        myrule.request_url = request_url
        self.assertEqual(myrule.request_url, request_url)

        # geography
        myrule.geography = geography
        self.assertEqual(myrule.geography, geography)
