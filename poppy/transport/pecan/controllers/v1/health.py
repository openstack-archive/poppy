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
from poppy.transport.pecan.models.response import health as health_response


class StorageHealthController(base.Controller):
    def __init__(self, driver):
        super(StorageHealthController, self).__init__(driver)

    @pecan.expose('json')
    def get(self, storage_name):
        """Returns the health of storage."""

        try:
            is_alive = self._driver.manager.is_storage_alive(storage_name)
            return health_response.StorageModel(is_alive)
        except KeyError:
            pecan.response.status = 404


class ProviderHealthController(base.Controller):
    def __init__(self, driver):
        super(ProviderHealthController, self).__init__(driver)

    @pecan.expose('json')
    def get(self, provider_name):
        """Returns the health of provider."""

        try:
            is_alive = self._driver.manager.is_provider_alive(provider_name)
            return health_response.ProviderModel(is_alive)
        except KeyError:
            pecan.response.status = 404


class HealthController(base.Controller):

    def __init__(self, driver):
        super(HealthController, self).__init__(driver)

    @pecan.expose('json')
    def get(self):
        """Returns the health of storage and providers."""

        is_alive, health_map = self._driver.manager.health()
        if not is_alive:
            pecan.response.status = 503

        return health_response.HealthModel(pecan.request, health_map)
