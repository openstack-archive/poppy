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

from poppy.manager import base
from poppy.model.helpers import provider_details


class DefaultServicesController(base.ServicesController):

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller

    def list(self, project_id, marker=None, limit=None):
        return self.storage_controller.list(project_id, marker, limit)

    def get(self, project_id, service_name):
        return self.storage_controller.get(project_id, service_name)

    def create(self, project_id, service_obj):
        flavor = self.flavor_controller.get(service_obj.flavorRef)
        providers = [p.provider_id for p in flavor.providers]
        service_name = service_obj.name

        self.storage_controller.create(
            project_id,
            service_obj)

        responders = []
        for provider in providers:
            responder = self.provider_wrapper.create(
                self._driver.providers[provider],
                service_obj)
            responders.append(responder)

        provider_details_dict = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' not in responder[provider_name]:
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            provider_service_id=responder[provider_name]['id'],
                            access_urls=[link['href'] for link in
                                         responder[provider_name]['links']])
                    )
                    if 'status' in responder[provider_name]:
                        provider_details_dict[provider_name].status = (
                            responder[provider_name]['status'])
                    else:
                        provider_details_dict[provider_name].status = (
                            'deployed')
                else:
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            error_info=responder[provider_name]['error_detail']
                        )
                    )
                    provider_details_dict[provider_name].status = 'failed'

        self.storage_controller.update_provider_details(project_id,
                                                        service_name,
                                                        provider_details_dict)

        return responders

    def update(self, project_id, service_name, service_obj):
        self.storage_controller.update(
            project_id,
            service_name,
            service_obj
        )

        provider_details = self.storage_controller.get_provider_details(
            project_id,
            service_name)
        return self._driver.providers.map(
            self.provider_wrapper.update,
            provider_details,
            service_obj)

    def delete(self, project_id, service_name):
        self.storage_controller.delete(project_id, service_name)

        provider_details = self.storage_controller.get_provider_details(
            project_id,
            service_name)
        return self._driver.providers.map(
            self.provider_wrapper.delete,
            provider_details)
