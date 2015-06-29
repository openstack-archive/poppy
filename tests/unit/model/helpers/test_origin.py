# -*- coding: utf-8 -*-
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

    @ddt.unpack
    @ddt.data({'origin_url': 'www.mydomain.com',
              'changed_origin_url': 'www.changed-domain.com'},
              {'origin_url': u'www.düsseldorf-Lörick.com',
              'changed_origin_url': u'www.düsseldorf.com'})
    def test_origin(self, origin_url, changed_origin_url):

        port = 80
        ssl = True
        myorigin = origin.Origin(origin=origin_url, hostheadertype="origin",
                                 hostheadervalue="", port=80, ssl=True)

        # test all properties
        # origin
        self.assertEqual(myorigin.origin, origin_url)
        myorigin.origin = changed_origin_url
        self.assertEqual(myorigin.origin, changed_origin_url)

        # port
        self.assertEqual(myorigin.port, port)
        myorigin.port = 443
        self.assertEqual(myorigin.port, 443)

        # ssl
        self.assertEqual(myorigin.ssl, ssl)
        myorigin.ssl = True
        self.assertEqual(myorigin.ssl, True)

        # rules
        self.assertEqual(myorigin.rules, [])
        myorigin.rules = []
        self.assertEqual(myorigin.rules, [])

        # my other origin
        my_other_origin = origin.Origin.init_from_dict({"origin": origin_url})
        self.assertEqual(my_other_origin.origin, origin_url)
