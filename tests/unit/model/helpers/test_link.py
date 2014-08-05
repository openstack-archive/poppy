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

from cdn.model.helpers import link
from tests.unit import base


@ddt.ddt
class TestLink(base.TestCase):

    def test_link(self):

        href = 'http://www.mywebsite.com/'
        rel = 'nofollow'
        mylink = link.Link(href, rel)

        # test all properties
        # href
        self.assertEqual(mylink.href, href)
        self.assertRaises(AttributeError, setattr, mylink, 'href', href)

        # rel
        self.assertEqual(mylink.rel, rel)
        self.assertRaises(AttributeError, setattr, mylink, 'href', rel)
