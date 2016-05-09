# Copyright (c) 2016 Rackspace, Inc.
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

"""Unittests for BlueFlood utils"""

from poppy.metrics.blueflood.utils import helper

from tests.unit import base


class TestBlueFloodUtils(base.TestCase):

    def setUp(self):
        super(TestBlueFloodUtils, self).setUp()
        self.url = 'https://www.metrics.com'

    def _almostequal(self, entity1, entity2, delta=1):
        if abs(entity1 - entity2) <= delta:
            return True
        else:
            return False

    def test_helper_set_qs_on_url(self):

        params = {
            'metricType': 'requestCount',
            'domain': 'poppy.org'
        }

        url_with_qs_set = helper.set_qs_on_url(self.url, **params)

        self.assertIn('metricType=requestCount', url_with_qs_set)
        self.assertIn('domain=poppy.org', url_with_qs_set)

    def test_helper_join_url(self):
        relative_url = 'requestCount'
        expected_url = self.url + '/' + relative_url
        self.assertEqual(helper.join_url(self.url, relative_url),
                         expected_url)

    def test_retrieve_last_relative_url(self):
        relative_url = 'requestCount'
        non_relative_url = self.url + '/' + relative_url
        self.assertEqual(helper.retrieve_last_relative_url(non_relative_url),
                         relative_url)

    def test_resolution_converter_seconds_to_enum_happy(self):
        seconds_series = ['0', '300', '1200', '3600', '14400', '86400']
        for seconds in seconds_series:
            helper.resolution_converter_seconds_to_enum(seconds)

    def test_resolution_converter_seconds_to_enum_exception(self):
        self.assertRaises(ValueError,
                          helper.resolution_converter_seconds_to_enum,
                          '12345')
