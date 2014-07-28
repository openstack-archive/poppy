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

import uuid

import pecan

from cdn.transport.pecan.controllers import base


class ServicesController(base.Controller):

    @pecan.expose('json')
    def get_all(self):
        tenant_id = pecan.request.context.to_dict()['tenant']
        services_controller = self._driver.manager.services_controller
        return services_controller.list(tenant_id)

    @pecan.expose('json')
    def get_one(self):
        tenant_id = pecan.request.context.to_dict()['tenant']
        services_controller = self._driver.manager.services_controller
        return services_controller.list(tenant_id)
