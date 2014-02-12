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

import falcon
import json


class HostsResource:
    def on_get(self, req, resp):
        """Handles GET requests
        """
        resp.status = falcon.HTTP_200  # This is the default status
        home_doc = [
            {
                'hostname': 'www.mywebsite.com',
                'description': 'My Sample Website'
            },
            {
                'hostname': 'www.myotherwebsite.com',
                'description': 'My Other Website'
            }
        ]

        resp.body = json.dumps(home_doc)
