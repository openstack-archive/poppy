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

"""Unittests for BlueFlood metrics service_controller."""

import datetime
import random
import time
import uuid

import ddt
import mock

from oslo_config import cfg
from oslo_context import context as context_utils

from poppy.metrics.blueflood import driver
from poppy.metrics.blueflood.utils import client
from poppy.metrics.blueflood.utils import errors
from tests.unit import base


class Response(object):

    def __init__(self, ok, url, text, json_dict):
        self.ok = ok
        self.url = url
        self.text = text
        self.json_dict = json_dict

    def json(self):
        return self.json_dict


@ddt.ddt
class TestBlueFloodServiceController(base.TestCase):

    def setUp(self):
        super(TestBlueFloodServiceController, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.metrics_driver = (
            driver.BlueFloodMetricsDriver(self.conf))

    @ddt.data('requestCount', 'bandwidthOut', 'httpResponseCode_1XX',
              'httpResponseCode_2XX', 'httpResponseCode_3XX',
              'httpResponseCode_4XX', 'httpResponseCode_5XX')
    def test_read(self, metric_name):
        project_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        domain_name = 'www.' + str(uuid.uuid4()) + '.com'
        to_timestamp = datetime.datetime.utcnow()
        from_timestamp = \
            (datetime.datetime.utcnow() - datetime.timedelta(days=1))
        context_utils.get_current = mock.Mock()
        context_utils.get_current().to_dict = \
            mock.Mock(return_value={'tenant': project_id,
                                    'auth_token': auth_token})
        with mock.patch.object(client.BlueFloodMetricsClient,
                               'async_requests',
                               auto_spec=True) as mock_async:
            timestamp1 = str(int(time.time()))
            timestamp2 = str(int(time.time()) + 100)
            timestamp3 = str(int(time.time()) + 200)
            json_dict = {
                'values': [
                    {
                        'timestamp': timestamp1,
                        'sum': 45
                    },
                    {
                        'timestamp': timestamp2,
                        'sum': 34
                    },
                    {
                        'timestamp': timestamp3,
                        'sum': 11
                    },
                ]
            }
            metric_names = []
            regions = ['Mock_region{0}'.format(i) for i in range(6)]
            for region in regions:
                metric_names.append('_'.join([metric_name, domain_name,
                                              region]))
            mock_async_responses = []
            for metric_name in metric_names:
                url = 'https://www.metrics.com/{0}/{1}'.format(
                    project_id, metric_name)
                res = Response(ok=True,
                               url=url,
                               text='success',
                               json_dict=json_dict)
                mock_async_responses.append(res)

            # NOTE(TheSriram): shuffle the order of responses
            random.shuffle(mock_async_responses)
            mock_async.return_value = mock_async_responses

            results = self.metrics_driver.services_controller.read(
                metric_names=metric_names,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                resolution='86400'
            )

            for result in results:
                metric_name, response = result
                self.assertIn(metric_name, metric_names)
                metric_names.remove(metric_name)
                self.assertEqual(response[timestamp1], 45)
                self.assertEqual(response[timestamp2], 34)
                self.assertEqual(response[timestamp3], 11)

    def test_format_results_exception(self):
        json_dict = {
            'this is a error': [
                {
                    'errorcode': 400,
                }
            ]
        }
        resp = Response(ok=True,
                        url='https://www.metrics.com',
                        text='success',
                        json_dict=json_dict)
        formatter = self.metrics_driver.services_controller._result_formatter
        self.assertRaises(errors.BlueFloodApiSchemaError, formatter, resp)
