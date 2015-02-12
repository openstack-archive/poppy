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

import perf_config as CONFIG


class PoppyTasks(locust.TaskSet):
    project_id = CONFIG.project_id
    headers = {"Content-Type": "application/json",
               "X-Project-ID": project_id,
               "Accept": "application/json",
               "X-Auth-Token": CONFIG.token}
    service_urls = []

    def __init__(self, *args, **kwargs):
        super(PoppyTasks, self).__init__(*args, **kwargs)
        # Create a service so everything doesn't fail initially
        self.post_service()

    @locust.task(CONFIG.create_service_weight)
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
            "name": service_name,
            "flavor_id": self._pick_flavor(),
            "origins": [{"origin": "mywebsite1.com",
                         "ssl": False,
                         "port": 443}]}

        response = self.client.post('/'+self.project_id+'/services',
                                    data=json.dumps(post_data),
                                    headers=self.headers,
                                    name="/{tenant}/services")
        if response.ok:
            service_url = response.headers['location'].split('.com/v1.0')[1]
            self.service_urls.append(service_url)

    @locust.task(CONFIG.update_service_weight)
    def update_service(self):
        # Update service
        if not self.service_urls:
            return

        patch_data_update = [{
            "op": "add",
            "path": "/domains/-",
            "value": {
                "domain": "newDomain.com",
                "protocol": "http"
            }
        }]
        service_url = random.choice(self.service_urls)
        self.client.patch(service_url,
                          data=json.dumps(patch_data_update),
                          headers=self.headers,
                          name="/{tenant}/services/{id}")

    @locust.task(CONFIG.delete_service_weight)
    def delete_service(self):
        # Delete service
        if not self.service_urls:
            return
        service_url = self.service_urls.pop()
        self.client.delete(service_url,
                           headers=self.headers,
                           name="/{tenant}/services/{id}")

    @locust.task(CONFIG.delete_asset_weight)
    def delete_asset(self):
        # Delete asset
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.delete(service_url + '/assets',
                           headers=self.headers,
                           params={'url': self._pick_asset()},
                           name="/{tenant}/services/{id}/assets")

    @locust.task(CONFIG.delete_all_assets_weight)
    def delete_all_assets(self):
        # Delete all assets
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.delete(service_url + '/assets',
                           headers=self.headers,
                           params={'all': True},
                           name="/{tenant}/services/{id}/assets")

    @locust.task(CONFIG.list_services_weight)
    def list_services(self):
        # List services
        self.client.get('/'+self.project_id+'/services',
                        headers=self.headers,
                        name="/{tenant}/services")

    @locust.task(CONFIG.get_service_weight)
    def get_service(self):
        # Get specific service
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.get(service_url,
                        headers=self.headers,
                        name="/{tenant}/services/{id}")

    @locust.task(CONFIG.list_flavors_weight)
    def list_flavors(self):
        # List flavors
        self.client.get('/' + self.project_id + '/flavors',
                        headers=self.headers,
                        name="/{tenant}/flavors")

    @locust.task(CONFIG.get_flavors_weight)
    def get_flavors(self):
        # Get flavors
        self.client.get('/' + self.project_id + '/flavors/' +
                        self._pick_flavor(),
                        headers=self.headers,
                        name="/{tenant}/flavors/{flavor}")

    def _pick_flavor(self):
        return random.choice(CONFIG.flavors)

    def _pick_asset(self):
        return '/index.html'


class PoppyLocust(locust.HttpLocust):

    host = CONFIG.host
    task_set = PoppyTasks
    min_wait = CONFIG.min_wait
    max_wait = CONFIG.max_wait
