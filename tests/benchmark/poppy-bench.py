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

import json
import uuid
import locust


class PoppyTasks(locust.TaskSet):

    @locust.task
    def post_service(self):

        service_name = str(uuid.uuid1())

        post_data = {
            "domains": [
                {"domain": "mywebsite.com"}, {"domain": "blog.mywebsite.com"}],
            "caching": [
                {"name": "default", "ttl": 3600},
                {"name": "home", "ttl": 1200,
                    "rules": [{"name": "index", "request_url": "/index.htm"}]}
            ],
            "flavorRef": "standard",
            "name": service_name,
            "origins": [
                {"origin": "mywebsite1.com", "ssl": False, "port": 443}]}

        self.client.post('/services', data=json.dumps(post_data))

        self.client.delete('/services/{0}'.format(service_name),
                           name='/v1.0/[service_name]')

    @locust.task
    def get_service(self):
        self.client.get('/service/service_name')

    @locust.task
    def patch_service(self):
        self.client.patch('/service/service_name')

    @locust.task
    def list_services(self):
        self.client.get('/services')

    @locust.task
    def list_flavors(self):
        self.client.get('/flavors')

    @locust.task
    def get_flavor(self):
        self.client.get('/flavors')


class PoppyLocust(locust.HttpLocust):
    host = "http://0.0.0.0:8888/v1.0"
    task_set = PoppyTasks
    min_wait = 1000
    max_wait = 1000
