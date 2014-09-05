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

import pecan

from poppy.transport.pecan.controllers import base
from poppy.transport.pecan.models.request import service as req_service_model
from poppy.transport.pecan.models.response import link
from poppy.transport.pecan.models.response import service as resp_service_model
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import service
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule


class ServicesController(base.Controller):

    @pecan.expose('json')
    def get_all(self):
        marker = pecan.request.GET.get('marker')
        limit = pecan.request.GET.get('limit')
        services_controller = self._driver.manager.services_controller
        service_resultset = services_controller.list(
            self.project_id, marker, limit)
        result = [
            resp_service_model.Model(s) for s in service_resultset]
        # TODO(tonytan4ever): edge case: what should be the result when there
        # is no service ? What should be the links field of return like ?
        return {
            'links': link.Model('/v1.0/services?marker={0}&limit={1}'.format(
                result[-1]["name"] if len(result) > 0 else None,
                limit),
                'next'),
            'services': result
        }

    @pecan.expose('json')
    def get_one(self, service_name):
        services_controller = self._driver.manager.services_controller
        service_obj = services_controller.get(self.project_id, service_name)
        # convert a service model into a response service model
        return resp_service_model.Model(service_obj)

    @pecan.expose('json')
    @decorators.validate(
        service_name=rule.Rule(
            helpers.is_valid_service_name(),
            helpers.abort_with_message),
        request=rule.Rule(
            helpers.json_matches_schema(
                service.ServiceSchema.get_schema("service", "PUT")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def put(self, service_name):
        services_controller = self._driver.manager.services_controller
        service_json_dict = json.loads(pecan.request.body.decode('utf-8'))
        service_obj = req_service_model.load_from_json(service_json_dict)
        return services_controller.create(self.project_id, service_name,
                                          service_obj)

    @pecan.expose('json')
    def delete(self, service_name):
        services_controller = self._driver.manager.services_controller
        return services_controller.delete(self.project_id, service_name)

    @pecan.expose('json')
    @decorators.validate(
        service_name=rule.Rule(
            helpers.is_valid_service_name(),
            helpers.abort_with_message),
        request=rule.Rule(
            helpers.json_matches_schema(
                service.ServiceSchema.get_schema("service", "PATCH")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def patch_one(self, service_name):
        services_controller = self._driver.manager.services_controller
        service_json = json.loads(pecan.request.body.decode('utf-8'))
        # TODO(tonytan4ever): convert service_json into a partial service model
        # under poppy.models.helpers.service.py
        # and pass service_json to update
        return services_controller.update(self.project_id, service_name,
                                          service_json)
