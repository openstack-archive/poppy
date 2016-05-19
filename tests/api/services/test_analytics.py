# coding= utf-8

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

import datetime
import uuid

import ddt
import hypothesis
from hypothesis.extra import datetime as hypothesis_datetime
from hypothesis import strategies

from tests.api import base
from tests.api.utils.schema import analytics


@ddt.ddt
class TestAnalytics(base.TestBase):

    """Tests for Analytics."""

    def setUp(self):
        super(TestAnalytics, self).setUp()

        self.flavor_id = self.test_flavor
        service_name = str(uuid.uuid1())

        self.domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        self.domain_list = [{"domain": self.domain}]

        self.origin_list = [{"origin": self.generate_random_string(
            prefix='api-test-origin') + '.com', "port": 80, "ssl": False,
            "hostheadertype": "custom", "hostheadervalue":
            "www.customweb.com"}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.log_delivery = {"enabled": False}

        resp = self.client.create_service(service_name=service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          log_delivery=self.log_delivery)

        self.location = resp.headers["location"]
        self.client.wait_for_service_status(
            location=self.location,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @ddt.data('requestCount', 'bandwidthOut', 'httpResponseCode_2XX',
              'httpResponseCode_3XX', 'httpResponseCode_4XX',
              'httpResponseCode_5XX')
    def test_analytics(self, metric_type):
        end_time = datetime.datetime.now()
        delta_days = datetime.timedelta(days=1)
        start_time = end_time - delta_days

        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        domain = self.domain

        resp = self.client.get_analytics(
            location=self.location, domain=domain, start_time=start_time_str,
            end_time=end_time_str, metric_type=metric_type)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        if metric_type == 'requestCount':
            self.assertSchema(body, analytics.get_request_count)
        elif metric_type == 'bandwidthOut':
            self.assertSchema(body, analytics.get_bandwidthOut)
        elif metric_type == 'httpResponseCode_2XX':
            self.assertSchema(body, analytics.get_httpResponseCode_2XX)
        elif metric_type == 'httpResponseCode_3XX':
            self.assertSchema(body, analytics.get_httpResponseCode_3XX)
        elif metric_type == 'httpResponseCode_4XX':
            self.assertSchema(body, analytics.get_httpResponseCode_4XX)
        elif metric_type == 'httpResponseCode_5XX':
            self.assertSchema(body, analytics.get_httpResponseCode_5XX)

    @ddt.data('requestCount', 'bandwidthOut', 'httpResponseCode_2XX',
              'httpResponseCode_3XX', 'httpResponseCode_4XX',
              'httpResponseCode_5XX')
    def test_analytics_no_endtime(self, metric_type):
        end_time = datetime.datetime.now()
        delta_days = datetime.timedelta(days=1)
        start_time = end_time - delta_days

        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        domain = self.domain

        resp = self.client.get_analytics(
            location=self.location, domain=domain, start_time=start_time_str,
            metric_type=metric_type)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        if metric_type == 'requestCount':
            self.assertSchema(body, analytics.get_request_count)
        elif metric_type == 'bandwidthOut':
            self.assertSchema(body, analytics.get_bandwidthOut)
        elif metric_type == 'httpResponseCode_2XX':
            self.assertSchema(body, analytics.get_httpResponseCode_2XX)
        elif metric_type == 'httpResponseCode_3XX':
            self.assertSchema(body, analytics.get_httpResponseCode_3XX)
        elif metric_type == 'httpResponseCode_4XX':
            self.assertSchema(body, analytics.get_httpResponseCode_4XX)
        elif metric_type == 'httpResponseCode_5XX':
            self.assertSchema(body, analytics.get_httpResponseCode_5XX)

    def tearDown(self):
        self.client.delete_service(location=self.location)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestAnalytics, self).tearDown()


@ddt.ddt
class TestAnalyticsHypothesis(base.TestBase):

    """Hypothesis Tests for Analytics."""

    def setUp(self):
        super(TestAnalyticsHypothesis, self).setUp()

        if self.test_config.run_hypothesis_tests is False:
            self.skipTest(
                'Hypothesis Tests are disabled in configuration')

        self.flavor_id = self.test_flavor
        service_name = str(uuid.uuid1())

        self.domain = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        self.domain_list = [{"domain": self.domain}]

        self.origin_list = [{"origin": self.generate_random_string(
            prefix='api-test-origin') + '.com', "port": 80, "ssl": False,
            "hostheadertype": "custom", "hostheadervalue":
            "www.customweb.com"}]

        self.caching_list = [{"name": "default", "ttl": 3600},
                             {"name": "home", "ttl": 1200,
                              "rules": [{"name": "index",
                                         "request_url": "/index.htm"}]}]
        self.log_delivery = {"enabled": False}

        resp = self.client.create_service(service_name=service_name,
                                          domain_list=self.domain_list,
                                          origin_list=self.origin_list,
                                          caching_list=self.caching_list,
                                          flavor_id=self.flavor_id,
                                          log_delivery=self.log_delivery)

        self.location = resp.headers["location"]
        self.client.wait_for_service_status(
            location=self.location,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @hypothesis.given(strategies.text())
    def test_analytics_negative_metric_type(self, metric_type):
        end_time = datetime.datetime.now()
        delta_days = datetime.timedelta(days=1)
        start_time = end_time - delta_days

        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        domain = self.domain

        resp = self.client.get_analytics(
            location=self.location, domain=domain, start_time=start_time_str,
            end_time=end_time_str, metric_type=metric_type)
        self.assertEqual(resp.status_code, 400)

    @hypothesis.given(strategies.text())
    def test_analytics_negative_domain(self, domain):
        end_time = datetime.datetime.now()
        delta_days = datetime.timedelta(days=1)
        start_time = end_time - delta_days

        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        metric_type = 'httpResponseCode_2XX'

        resp = self.client.get_analytics(
            location=self.location, domain=domain, start_time=start_time_str,
            end_time=end_time_str, metric_type=metric_type)
        self.assertEqual(resp.status_code, 400)

    #  the datetime strftime() methods requires year >= 1900
    @hypothesis.given(hypothesis_datetime.datetimes(min_year=1900),
                      hypothesis_datetime.datetimes(min_year=1900))
    def test_analytics_negative_time_range(self, start_time, end_time):
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        metric_type = 'requestCount'
        domain = self.domain

        resp = self.client.get_analytics(
            location=self.location, domain=domain, start_time=start_time_str,
            end_time=end_time_str, metric_type=metric_type)
        # Verify that we never get back a HTTP 500
        self.assertIn(resp.status_code, [200, 400])

    def tearDown(self):
        self.client.delete_service(location=self.location)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestAnalyticsHypothesis, self).tearDown()
