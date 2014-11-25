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

import requests


class WebpageTestClient(object):

    def __init__(self, wpt_url, api_key):
        self.wpt_url = wpt_url
        self.api_key = api_key

    def start_test(self, access_url, test_location, runs=5):
        """Starts webpage test

        :param access_url: the url which needs performance metrics
        :param test_location: location to run the test on
        :param runs: number of test runs
        :returns: url to access the test details
        """
        start_url = self.wpt_url + '/runtest.php?url=' + access_url + \
            '&k=' + self.api_key + '&location=' + test_location + \
            '&runs=' + str(runs) + '&f=json'
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
