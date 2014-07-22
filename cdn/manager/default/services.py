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

from cdn.manager import base


class DefaultServicesController(base.ServicesController):
    def __init__(self, driver):
        super(DefaultServicesController, self).__init__(driver)

        self.services_controller = self._driver.storage.service_controller

    def list(self, project_id):
        return self.services_controller.list(project_id)

    def get(self, project_id, service_name):
        return self.services_controller.get(project_id, service_name)

    def create(self, project_id, service_name, service_json):
        self.services_controller.create(
            project_id,
            service_name,
            service_json)

        if (self._driver.providers is not None):
            return self._driver.providers.map(
                self.provider_wrapper.create,
                service_name,
                service_json)
        else:
            return None

    def update(self, project_id, service_name, service_json):
        self.services_controller.update(
            project_id,
            service_name,
            service_json
        )

        if (self._driver.providers is not None):
            return self._driver.providers.map(
                self.provider_wrapper.update,
                service_name,
                service_json)
        else:
            return None

    def delete(self, project_id, service_name):
        self.services_controller.delete(project_id, service_name)

        if (self._driver.providers is not None):
            return self._driver.providers.map(
                self.provider_wrapper.delete,
                service_name)
        else:
            return None
