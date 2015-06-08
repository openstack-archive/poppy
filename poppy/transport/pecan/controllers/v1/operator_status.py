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

import pecan
from pecan import hooks

from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks


class OperatorStatusController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    @pecan.expose('json')
    def get(self):
        services_controller = self._driver.manager.services_controller
        try:
            service_obj = services_controller.get(
                self.project_id, service_id)
        except ValueError:
            pecan.abort(404, detail='service %s could not be found' %
                        service_id)
        # convert a service model into a response service model
        return resp_service_model.Model(service_obj, self)

class ServiceController(base.Controller, hooks.HookController):

    state = OperatorStatusController()
