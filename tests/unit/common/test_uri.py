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

from poppy.common import uri
from tests.unit import base


class URITest(base.TestCase):

    def test_uri_encode(self):
        url = 'http://example.com/v1/fizbit/messages?limit=3&echo=true'
        self.assertEqual(uri.encode(url), url)

        url = 'http://example.com/v1/fiz bit/messages'
        expected = 'http://example.com/v1/fiz%20bit/messages'
        self.assertEqual(uri.encode(url), expected)

        url = u'http://example.com/v1/fizbit/messages?limit=3&e\u00e7ho=true'
        expected = ('http://example.com/v1/fizbit/messages'
                    '?limit=3&e%C3%A7ho=true')
        self.assertEqual(uri.encode(url), expected)

    def test_uri_encode_value(self):
        self.assertEqual(uri.encode_value('abcd'), 'abcd')
        self.assertEqual(uri.encode_value(u'abcd'), u'abcd')
        self.assertEqual(uri.encode_value(u'ab cd'), u'ab%20cd')
        self.assertEqual(uri.encode_value(u'\u00e7'), '%C3%A7')
        self.assertEqual(uri.encode_value(u'\u00e7\u20ac'),
                         '%C3%A7%E2%82%AC')
        self.assertEqual(uri.encode_value('ab/cd'), 'ab%2Fcd')
        self.assertEqual(uri.encode_value('ab+cd=42,9'),
                         'ab%2Bcd%3D42%2C9')
