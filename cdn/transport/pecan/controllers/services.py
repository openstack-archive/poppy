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

from cdn.openstack.common import local
from cdn.transport.pecan.controllers import base


class ServicesController(base.Controller):

    @pecan.expose('json')
    def get_all(self):
        context = local.store.context
        tenant_id = context.tenant
        marker = pecan.request.GET.get('marker')
        limit = pecan.request.GET.get('limit')
        services_controller = self._driver.manager.services_controller
        return services_controller.list(tenant_id, marker, limit)

    @pecan.expose('json')
    def get_one(self, service_name):
        context = local.store.context
        tenant_id = context.tenant
        services_controller = self._driver.manager.services_controller
        return services_controller.get(tenant_id, service_name)

    @pecan.expose('json')
    def put(self, service_name):
        context = local.store.context
        tenant_id = context.tenant
        services_controller = self._driver.manager.services_controller
        service_json = json.loads(pecan.request.body.decode('utf-8'))
        return services_controller.create(tenant_id, service_name,
                                                        service_json)

    @pecan.expose('json')
    def delete(self, service_name):
        context = local.store.context
        tenant_id = context.tenant
        services_controller = self._driver.manager.services_controller
        return services_controller.delete(tenant_id, service_name)

    @pecan.expose('json')
    def patch_one(self, service_name):
        context = local.store.context
        tenant_id = context.tenant
        services_controller = self._driver.manager.services_controller
        service_json = json.loads(pecan.request.body.decode('utf-8'))
        return services_controller.update(tenant_id, service_name,
                                                        service_json)
