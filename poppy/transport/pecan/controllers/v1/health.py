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


class HealthController(base.Controller):

    def __init__(self, driver):
        super(HealthController, self).__init__(driver)

    def get_health_storage(self):
        """Returns the health of storage."""

        body = {}
        storage_name, is_alive = self._driver.manager.health_storage()
        if is_alive:
            pecan.response.status = 200
            body['online'] = 'true'
        else:
            pecan.response.status = 503
            body['online'] = 'false'

        return body

    def get_health_provider(self, provider_name):
        """Returns the health of provider."""

        body = {}
        try:
            _, is_alive = self._driver.manager.health_provider(provider_name)
        except KeyError:
            pecan.abort(204)

        if is_alive:
            pecan.response.status = 200
            body['online'] = 'true'
        else:
            pecan.response.status = 503
            body['online'] = 'false'

        return body

    @pecan.expose('json')
    def get(self, *args):
        """Returns the health of storage and providers."""

        if args:
            if args[0] == 'storage':
                return self.get_health_storage()
            else:
                return self.get_health_provider(args[0])

        base_url = 'https://www.poppycdn.io/health'
        links = {
            'href': '',
            'rel': 'self'
        }
        status = 200
        body = {}

        health_storage = {}
        storage_name, is_alive = self._driver.manager.health_storage()

        if is_alive:
            health_storage['online'] = 'true'
        else:
            status = 503
            health_storage['online'] = 'false'
        links['href'] = base_url + '/storage/' + storage_name
        health_storage['links'] = links
        body['storage'] = {storage_name: health_storage}

        body['providers'] = []
        health_providers = self._driver.manager.health_providers()
        for provider_name, is_alive in health_providers:
            health_provider = {}
            if is_alive:
                health_provider['online'] = 'true'
            else:
                status = 503
                health_provider['online'] = 'false'
            links['href'] = base_url + '/provider/' + provider_name
            health_provider['links'] = links
            body['providers'].append({provider_name: health_provider})

        pecan.response.status = status

        return body
