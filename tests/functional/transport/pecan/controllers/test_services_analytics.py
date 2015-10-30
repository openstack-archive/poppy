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

import datetime
import urllib
import uuid

import ddt

from tests.functional.transport.pecan import base


@ddt.ddt
class TestServicesAnalytics(base.FunctionalTest):

    def setUp(self):
        super(TestServicesAnalytics, self).setUp()

        self.project_id = str(uuid.uuid1())
        self.service_id = str(uuid.uuid1())
        self.endTime = datetime.datetime.now()
        self.startTime = self.endTime - datetime.timedelta(hours=3)

    def test_services_analytics_happy_path_with_default_timewindow(self):
        response = self.app.get('/v1.0/services/%s/analytics' %
                                self.service_id,
                                params=urllib.urlencode({
                                    'domain': 'abc.com',
                                    'metric': 'requestCount',
                                }),
                                headers={
                                    'X-Project-ID': self.project_id
                                })

        self.assertEqual(response.status_code, 200)

    def test_services_analytics_happy_path(self):
        response = self.app.get('/v1.0/services/%s/analytics' %
                                self.service_id,
                                params=urllib.urlencode({
                                    'domain': 'abc.com',
                                    'metric': 'requestCount',
                                    'startTime': datetime.datetime.strftime(
                                        self.startTime, "%Y-%m-%dT%H:%M:%S"),
                                    'endTime': datetime.datetime.strftime(
                                        self.endTime, "%Y-%m-%dT%H:%M:%S")
                                }),
                                headers={
                                    'X-Project-ID': self.project_id
                                })

        self.assertEqual(response.status_code, 200)

    @ddt.file_data("data_services_analytics_bad_input.json")
    def test_services_analytics_negative(self, get_params):
        response = self.app.get('/v1.0/services/%s/analytics' %
                                self.service_id,
                                params=urllib.urlencode(get_params),
                                headers={
                                    'X-Project-ID': self.project_id
                                },
                                expect_errors=True)

        self.assertEqual(response.status_code, 400)
