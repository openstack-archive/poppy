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

    @pecan.expose('json')
    def get(self, storage_name):
        """Returns the health of storage."""

        health_controller = self._driver.manager.health_controller

        try:
            is_alive = health_controller.is_storage_alive(storage_name)
            return health_response.StorageModel(is_alive)
        except KeyError:
            pecan.response.status = 404


class ProviderHealthController(base.Controller):

    @pecan.expose('json')
    def get(self, provider_name):
        """Returns the health of provider."""

        health_controller = self._driver.manager.health_controller

        try:
            is_alive = health_controller.is_provider_alive(provider_name)
            return health_response.ProviderModel(is_alive)
        except KeyError:
            pecan.response.status = 404


class HealthController(base.Controller):

    @pecan.expose('json')
    def get(self):
        """Returns the health of storage and providers."""

        health_controller = self._driver.manager.health_controller

        is_alive, health_map = health_controller.health()
        if not is_alive:
            pecan.response.status = 503

        return health_response.HealthModel(pecan.request, health_map)
