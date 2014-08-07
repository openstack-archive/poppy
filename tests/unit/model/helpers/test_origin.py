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

from poppy.model.helpers import origin
from tests.unit import base


@ddt.ddt
class TestOrigin(base.TestCase):

    def test_origin(self):

        origin_url = 'www.mywebsite.com'
        port = 443
        ssl = True
        myorigin = origin.Origin(origin_url, port, ssl)

        # test all properties
        # origin
        self.assertEqual(myorigin.origin, origin_url)
        self.assertRaises(
            AttributeError, setattr, myorigin, 'origin', origin_url)

        # port
        self.assertEqual(myorigin.port, port)
        myorigin.port = 80
        self.assertEqual(myorigin.port, 80)

        # ssl
        self.assertEqual(myorigin.ssl, ssl)
        myorigin.ssl = True
        self.assertEqual(myorigin.ssl, True)

        # rules
        self.assertEqual(myorigin.rules, [])
        self.assertRaises(AttributeError, setattr, myorigin, 'rules', [])
