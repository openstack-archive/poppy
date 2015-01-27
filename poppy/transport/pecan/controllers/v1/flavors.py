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
from pecan import hooks

from poppy.common import uri
from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.pecan.models.request import flavor as flavor_request
from poppy.transport.pecan.models.response import flavor as flavor_response
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import flavor as schema
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule


class FlavorsController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    """Flavors Controller."""

    @pecan.expose('json')
    def get_all(self):
        """get all flavor list."""

        flavors_controller = self.driver.manager.flavors_controller
        result = flavors_controller.list()

        flavor_list = [
            flavor_response.Model(item, self) for item in result]

        return {
            'flavors': flavor_list
        }

    @pecan.expose('json')
    @decorators.validate(
        flavor_id=rule.Rule(
            helpers.is_valid_flavor_id(),
            helpers.abort_with_message)
    )
    def get_one(self, flavor_id):
        """get_one

        :param flavor_model
        :returns JSON flavor(HTTP 200) or HTTP 404
        """
        flavors_controller = self.driver.manager.flavors_controller
        try:
            result = flavors_controller.get(flavor_id)
        except LookupError as e:
            pecan.abort(404, detail=str(e))
        else:
            return flavor_response.Model(result, self)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_flavor_schema(
                schema.FlavorSchema.get_schema("flavor", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        """POST

        :returns JSON flavor(HTTP 200) or HTTP 400
        """
        flavors_controller = self.driver.manager.flavors_controller
        flavor_json = json.loads(pecan.request.body.decode('utf-8'))
        try:
            new_flavor = flavor_request.load_from_json(flavor_json)
            flavors_controller.add(new_flavor)

            # form the success response
            flavor_url = str(
                uri.encode(u'{0}/flavors/{1}'.format(
                    self.base_url,
                    new_flavor.flavor_id)))
            pecan.response.status = 201
            pecan.response.headers["Location"] = flavor_url

            result = flavors_controller.get(new_flavor.flavor_id)
            return flavor_response.Model(result, self)

        except Exception as e:
            pecan.abort(400, detail=str(e))

    @pecan.expose('json')
    def delete(self, flavor_id):
        """DELETE

        :param flavor_model
        :returns HTTP 204
        """
        flavors_controller = self.driver.manager.flavors_controller
        flavors_controller.delete(flavor_id)
        pecan.response.status = 204
