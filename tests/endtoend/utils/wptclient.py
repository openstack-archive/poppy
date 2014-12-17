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

import time

import requests


class WebpageTestClient(object):

    def __init__(self, wpt_url, api_key):
        self.wpt_url = wpt_url
        self.api_key = api_key

    def start_test(self, test_url, test_location, runs=5):
        """Starts webpage test

        :param test_url: the url which needs performance metrics
        :param test_location: location to run the test on
        :param runs: number of test runs
        :returns: url to access the test details
        """
        start_url = (self.wpt_url + '/runtest.php?url=' + test_url +
                     '&k=' + self.api_key + '&location=' + test_location +
                     '&runs=' + str(runs) + '&f=json')
        response = requests.post(start_url)
        test = response.json()
        return test['data']['jsonUrl']

    def get_test_details(self, test_url):
        """Gets test results in json format

        :param test_url: the url pointing to json test results
        :returns: test details json
        """
        response = requests.get(test_url)
        return response.json()

    def wait_for_test_status(self, test_url, status='COMPLETE',
                             retry_timeout=6000, retry_interval=10):

        """Waits for the wpt test to be completed.

        :param test_url: the url pointing to json test results
        :param status: expected status from WPT server
            200 (COMPLETE) indicates test is completed.
            1XX means the test is still in progress.
            And 4XX indicates some error.
        """
        current_status = ''
        start_time = int(time.time())
        stop_time = start_time + retry_timeout
        if status == 'COMPLETE':
            status_code = 200
        while current_status != status:
            time.sleep(retry_interval)
            test_details = self.get_test_details(test_url=test_url)
            current_status = test_details['statusCode']
            print('status', test_details)
            if (current_status == status_code):
                return
            current_time = int(time.time())
            if current_time > stop_time:
                return
