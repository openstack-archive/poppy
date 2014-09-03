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

from poppy.transport.pecan.controllers import base


class HealthProviderController(base.Controller):
    @pecan.expose('json')
    def get(self):
        provider = pecan.request.path.split('/')[-1]
        status, body = self._driver.manager.health_provider(provider)
        pecan.response.status = status
        return body


class HealthStorageController(base.Controller):
    @pecan.expose('json')
    def get(self):
        status, body = self._driver.manager.health_storage()
        pecan.response.status = status
        return body


class HealthController(base.Controller):
    def __init__(self, driver):
        super(HealthController, self).__init__(driver)

        self.add_controller('storage', HealthStorageController(driver))
        providers_controller = HealthProviderController(driver)
        for provider in driver.manager.providers:
            self.add_controller(provider.obj.provider_name.lower(),
                                providers_controller)

    @pecan.expose('json')
    def get(self):
        status, body = self._driver.manager.health()
        pecan.response.status = status
        return body
