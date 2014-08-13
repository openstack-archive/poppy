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

import falcon


class ServicesResource:
    def __init__(self, services_controller):
        self.services_controller = services_controller

    def on_get(self, req, resp, project_id):
        """Handles GET requests."""

        services = self.services_controller.list(project_id)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(services)


class ServiceResource:
    def __init__(self, service_controller):
        self.service_controller = service_controller

    def on_get(self, req, resp, project_id, service_name):
        """Handles GET requests."""

        service = self.service_controller.get(project_id, service_name)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(service)

    def on_put(self, req, resp, project_id, service_name):
        """Handles PUT requests."""

        service_json = json.loads(req.stream.read(req.content_length))

        service = self.service_controller.create(project_id,
                                                 service_name,
                                                 service_json)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(service)

    def on_patch(self, req, resp, project_id, service_name):
        """Handles PATCH requests."""

        service = self.service_controller.update(project_id, service_name)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(service)

    def on_delete(self, req, resp, project_id, service_name):
        """Handles DELETE requests."""

        service = self.service_controller.delete(project_id, service_name)
        resp.status = falcon.HTTP_204
        resp.body = json.dumps(service)
