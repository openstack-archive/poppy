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


class DefaultServicesController(base.ServicesController):
    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage = self._driver.storage.services_controller

    def list(self, project_id, marker=None, limit=None):
        return self.storage.list(project_id, marker, limit)

    def get(self, project_id, service_name):
        return self.storage.get(project_id, service_name)

    def create(self, project_id, service_name, service_json):
        self.storage.create(
            project_id,
            service_name,
            service_json)

        return self._driver.providers.map(
            self.provider_wrapper.create,
            service_name,
            service_json)

    def update(self, project_id, service_name, service_json):
        self.storage.update(
            project_id,
            service_name,
            service_json
        )

        return self._driver.providers.map(
            self.provider_wrapper.update,
            service_name,
            service_json)

    def delete(self, project_id, service_name):
        self.storage.delete(project_id, service_name)

        return self._driver.providers.map(
            self.provider_wrapper.delete,
            service_name)
