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


class PingController(base.Controller, hooks.HookController):

    # no poppy_hooks.Context() required here as
    # project_id is not required to be submitted
    __hooks__ = [poppy_hooks.Error()]

    @pecan.expose('json')
    def get(self):
        health_controller = self._driver.manager.health_controller
        health_map, is_alive = health_controller.ping_check()
        if is_alive:
            return pecan.Response(None, 204)
        else:
            return pecan.Response(None, 503)
