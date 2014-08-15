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
from poppy.transport.pecan.models.request import flavor as flavor_request
from poppy.transport.pecan.models.response import flavor as flavor_response


class FlavorsController(base.Controller):

    @pecan.expose('json')
    def get_all(self):
        flavors_controller = self._driver.manager.flavors_controller
        result = flavors_controller.list()

        flavor_list = [flavor_response.Model(item) for item in result]

        return flavor_list

    @pecan.expose('json')
    def get_one(self, flavor_id):
        flavors_controller = self._driver.manager.flavors_controller
        result = flavors_controller.get(flavor_id)

        return flavor_response.Model(result[0])

    @pecan.expose('json')
    def put(self, flavor_id):
        flavors_controller = self._driver.manager.flavors_controller
        flavor_json = json.loads(pecan.request.body.decode('utf-8'))

        flavor = flavor_request.Model(flavor_json)
        flavors_controller.add(flavor)

    @pecan.expose('json')
    def delete(self, flavor_id):
        flavors_controller = self._driver.manager.flavors_controller
        flavors_controller.delete(flavor_id)
