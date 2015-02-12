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
import locust
import random
import uuid


class PoppyTasks(locust.TaskSet):
    tenant_id = "862456"
    token = "xxxxxxx"
    headers = {"Content-Type": "application/json",
               "X-Project-ID": tenant_id,
               "Accept": "application/json",
               "X-Auth-Token": token}
    service_ids = []

    @locust.task(2)
    def post_service(self):
        # Create service
        service_name = str(uuid.uuid1())
        domain_name = "qe_blog"+service_name

        post_data = {
            "domains": [{"domain": domain_name+"mywebsite3.com"},
                        {"domain": domain_name+".mywebsite.com"}],
            "caching": [{"name": "default", "ttl": 3600},
                        {"name": "home", "ttl": 1200,
                         "rules": [{"name": "index",
                                    "request_url": "/index.htm"}]}],
            "flavorRef": "standard", "name": service_name, "flavor_id": "cdn",
            "origins": [{"origin": "mywebsite1.com",
                         "ssl": False,
                         "port": 443}]}

        response = self.client.post('/'+self.tenant_id+'/services',
                                    data=json.dumps(post_data),
                                    headers=self.headers)
        service_id = response.headers['location'].split('/')[-1]
        self.service_ids.append(service_id)

    @locust.task(1)
    def update_service(self):
        # Update service
        patch_data_update = [{
            "op": "add",
            "path": "/domains/-",
            "value": {
                "domain": "newDomain.com",
                "protocol": "http"
            }
        }]
        service_id = self.service_ids.pop()
        self.client.patch('/'+self.tenant_id+'/services/'
                                            + service_id,
                          data=json.dumps(patch_data_update),
                          headers=self.headers)
        self.service_ids.put(service_id)

    @locust.task(1)
    def delete_service(self):
        # Delete service
        service_id = self.service_ids.pop()
        self.client.delete('/'+self.tenant_id+'/services/'
                                             + service_id,
                           headers=self.headers)

    @locust.task(10)
    def delete_asset(self):
        # Delete asset
        service_id = self.service_ids.pop()
        self.client.delete('/'+self.tenant_id+'/services/'+service_id
                           + '/assets',
                           headers=self.headers,
                           params={'url': self._pick_asset()})
        self.service_ids.put(service_id)

    @locust.task(10)
    def delete_all_assets(self):
        # Delete all assets
        service_id = self.service_ids.pop()
        self.client.delete('/'+self.tenant_id+'/services/'+service_id
                           + '/assets',
                           headers=self.headers,
                           params={'all': True})
        self.service_ids.put(service_id)

    @locust.task(20)
    def list_services(self):
        # List services
        self.client.get('/'+self.tenant_id+'/services', headers=self.headers)

    @locust.task(10)
    def get_service(self):
        # Get specific service
        service_id = self.service_ids.pop()
        self.client.get('/'+self.tenant_id+'/services/'+service_id,
                        headers=self.headers)
        self.service_ids.put(service_id)

    @locust.task(4)
    def list_flavors(self):
        # List flavors
        self.client.get('/'+self.tenant_id+'/flavors', headers=self.headers)

    @locust.task(4)
    def get_flavors(self):
        # Get flavors
        self.client.get('/'+self.tenant_id+'/flavors/'+self._pick_flavor(),
                        headers=self.headers)

    def _pick_flavor(self):
        # pick a random flavor
        return random.choice(('cdn', 'երանգ'))

    def _pick_asset(self):
        # pick an asset
        return '/index.html'


class PoppyLocust(locust.HttpLocust):

    host = "http://0.0.0.0:8888/v1.0"
    task_set = PoppyTasks
    min_wait = 1000
    max_wait = 1000
