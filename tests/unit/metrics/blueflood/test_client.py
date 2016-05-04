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

"""Unittests for BlueFlood client"""


import uuid

from mock import MagicMock

from poppy.metrics.blueflood.utils import client

from tests.unit import base

import requests_mock


class ResponseMocked(object):

    def __init__(self):
        self.status_code = 200
        self.text = 'Success'


class TestBlueFloodClient(base.TestCase):

    def setUp(self):
        super(TestBlueFloodClient, self).setUp()
        self.project_id = uuid.uuid4()
        self.token = uuid.uuid4()
        self.executors = 5
        self.headers = {
            'X-Project-ID': self.project_id,
            'X-Auth-Token': self.token
        }
        self.bf_client = client.BlueFloodMetricsClient(
            project_id=self.project_id,
            token=self.token,
            executors=self.executors
        )

        self.mockedResponse = ResponseMocked()
        self.bf_client.async_requests = MagicMock(
            return_value=self.mockedResponse)

    def test_client_init(self):

        self.assertEqual(self.project_id, self.bf_client.project_id)
        self.assertEqual(self.token, self.bf_client.token)
        self.assertEqual(
            sorted(self.headers.items()),
            sorted(self.bf_client.headers.items()))

    def test_client_async_results(self):
        results = []
        re_ordered_urls = []
        urls = ["http://blueflood.com/{0}/views/{1}".format(
            self.project_id, i) for i in range(10)]
        with requests_mock.mock() as req_mock:
            for url in urls:
                req_mock.get(url, text='Success')
            for url in urls:
                results.append(self.bf_client.async_requests(url))
                re_ordered_urls.append(url)
            for result in results:
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.text, 'Success')
            self.assertEqual(sorted(urls), sorted(re_ordered_urls))
