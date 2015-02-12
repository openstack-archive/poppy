# Copyright (c) 2015 Rackspace, Inc.
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
    headers = {"Content-Type": "application/json",
               "X-Project-ID": CONFIG.project_id,
               "Accept": "application/json",
               "X-Auth-Token": CONFIG.token}
    service_urls = []

    def __init__(self, *args, **kwargs):
        super(PoppyTasks, self).__init__(*args, **kwargs)
        # Create a service so everything doesn't fail initially
        self.post_service()

    @locust.task(CONFIG.create_service)
    def post_service(self):
        # Create service
        service_name = str(uuid.uuid1())
        domain_name = "qe_blog" + service_name

        post_data = {
            "domains": [{"domain": domain_name}],
            "caching": [{"name": "default", "ttl": 3600},
                        {"name": "home", "ttl": 1200,
                         "rules": [{"name": "index",
                                    "request_url": "/index.htm"}]}],
            "flavor_id": CONFIG.flavor,
            "name": service_name,
            "origins": [{"origin": "104.130.27.124", "ssl": False, "port": 80}]
        }

        response = self.client.post('/services',
                                    data=json.dumps(post_data),
                                    headers=self.headers,
                                    name="/services")
        if response.ok:
            service_id = response.headers['location'].split('/services/')[1]
            service_url = '/services/' + service_id
            self.service_urls.append(service_url)

    @locust.task(CONFIG.update_service_domain)
    def update_service_domain(self):
        # Update a service's domains
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
                          name="/services/{id}")

    @locust.task(CONFIG.update_service_rule)
    def update_service_rule(self):
        # Update a service's rules
        if not self.service_urls:
            return

        patch_data = [{
            "op": "replace",
            "path": "/caching/0",
            "value": {
                "name": "home",
                "ttl": random.randint(500, 2500),
            }
        }]

        service_url = random.choice(self.service_urls)
        self.client.patch(service_url,
                          data=json.dumps(patch_data),
                          headers=self.headers,
                          name="/services/{id}")

    @locust.task(CONFIG.update_service_origin)
    def update_service_origin(self):
        # Update a service's origin
        if not self.service_urls:
            return

        random_origin = "mywebsite{0}.com.".format(random.randint(1000000000,
                                                                  9999999999))
        patch_data = [{
            "op": "replace",
            "path": "/origins/0",
            "value": {
                "origin": random_origin,
                "port": 80,
                "rules": [],
                "ssl": False
            }
        }]
        service_url = random.choice(self.service_urls)
        self.client.patch(service_url,
                          data=json.dumps(patch_data),
                          headers=self.headers,
                          name="/services/{id}")

    @locust.task(CONFIG.delete_service)
    def delete_service(self):
        # Delete service
        if not self.service_urls:
            return
        service_url = self.service_urls.pop()
        self.client.delete(service_url,
                           headers=self.headers,
                           name="/services/{id}")

    @locust.task(CONFIG.delete_asset)
    def delete_asset(self):
        # Delete asset
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.delete(service_url + '/assets',
                           headers=self.headers,
                           params={'url': self._pick_asset()},
                           name="/services/{id}/assets?url={asset}")

    @locust.task(CONFIG.delete_all_assets)
    def delete_all_assets(self):
        # Delete all assets
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.delete(service_url + '/assets',
                           headers=self.headers,
                           params={'all': True},
                           name="/services/{id}/assets?all=true")

    @locust.task(CONFIG.list_services)
    def list_services(self):
        # List services
        self.client.get('/services',
                        headers=self.headers,
                        name="/services")

    @locust.task(CONFIG.get_service)
    def get_service(self):
        # Get specific service
        if not self.service_urls:
            return
        service_url = random.choice(self.service_urls)
        self.client.get(service_url,
                        headers=self.headers,
                        name="/services/{id}")

    @locust.task(CONFIG.list_flavors)
    def list_flavors(self):
        # List flavors
        self.client.get('/flavors',
                        headers=self.headers,
                        name="/flavors")

    @locust.task(CONFIG.get_flavors)
    def get_flavors(self):
        # Get flavors
        self.client.get('/flavors/{0}'.format(CONFIG.flavor),
                        headers=self.headers,
                        name='/flavors/{0}'.format(CONFIG.flavor))

    def _pick_asset(self):
        return '/index.html'


class PoppyLocust(locust.HttpLocust):

    host = ("{0}/{1}".format(CONFIG.host, CONFIG.project_id)
            if CONFIG.project_id_in_url else CONFIG.host)
    task_set = PoppyTasks
    min_wait = CONFIG.min_wait
    max_wait = CONFIG.max_wait
