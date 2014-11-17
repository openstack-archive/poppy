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


class HomeController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    @pecan.expose('json')
    def get(self):
        home_controller = self._driver.manager.home_controller
        return home_controller.get()
