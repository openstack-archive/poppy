#su Copyright (c) 2014 Rackspace, Inc.
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

import json
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
import uuid

from poppy.transport.pecan.controllers import base as c_base
from tests.functional.transport.pecan import base


class ServiceControllerTest(base.FunctionalTest):

    def setUp(self):
        super(ServiceControllerTest, self).setUp()

        self.project_id = str(uuid.uuid1())
        self.service_name = str(uuid.uuid1())
        self.flavor_id = str(uuid.uuid1())

        # create a mock flavor to be used by new service creations
        flavor_json = {
            "id": self.flavor_id,
            "providers": [
                {
                    "provider": "mock",
                    "links": [
                        {
                            "href": "http://mock.cdn",
                            "rel": "provider_url"
                        }
                    ]
                }
            ]
        }
        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(flavor_json),
                                 headers={
                                     "Content-Type": "application/json",
                                     "X-Project-ID": self.project_id})

        self.assertEqual(201, response.status_code)

        # create an initial service to be used by the tests
        self.service_json = {
            "name": self.service_name,
            "domains": [
                {"domain": "test.mocksite.com"},
                {"domain": "blog.mocksite.com"}
            ],
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 80,
                    "ssl": False
                }
            ],
            "flavor_id": self.flavor_id,
            "caching": [
                {
                    "name": "default",
                    "ttl": 3600
                }
            ],
            "restrictions": [
                {
                    "name": "website only",
                    "type": "whitelist",
                    "rules": [
                        {
                            "name": "mocksite.com",
                            "http_host": "www.mocksite.com"
                        }
                    ]
                }
            ]
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(self.service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)
        self.assertTrue('Location' in response.headers)

        self.service_url = urlparse.urlparse(response.headers["Location"]).path

    def tearDown(self):
        super(ServiceControllerTest, self).tearDown()
