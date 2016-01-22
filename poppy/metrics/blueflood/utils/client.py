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

from requests_futures.sessions import FuturesSession


class BlueFloodMetricsClient(object):

    def __init__(self, token, project_id):
        self.token = token
        self.project_id = project_id
        self.session = FuturesSession(max_workers=10)
        self.headers = {
            'X-Project-ID': self.project_id
        }
        if self.token:
            self.headers.update({
                'X-Auth-Token': self.token
            })
        self.session.headers.update(self.headers)

    def async_requests(self, urls):
        futures = []
        for url in urls:
            futures.append(self.session.get(url))

        responses = []
        for future in futures:
            responses.append((future.result()))

        return responses
