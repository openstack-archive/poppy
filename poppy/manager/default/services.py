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

import multiprocessing
import uuid

from poppy.manager import base
from poppy.manager.default.service_async_workers import create_service_worker
from poppy.manager.default.service_async_workers import delete_service_worker


class DefaultServicesController(base.ServicesController):

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller

    def list(self, project_id, marker=None, limit=None):
        return self.storage_controller.list(project_id, marker, limit)

    def get(self, project_id, service_name):
        return self.storage_controller.get(project_id, service_name)

    def create(self, project_id, service_obj, service_json):
        try:
            flavor = self.flavor_controller.get(service_obj.flavorRef)
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        try:
            self.storage_controller.create(
                project_id,
                service_obj)
        # ValueError will be raised if the service has already existed
        except ValueError as e:
            raise e

        message = {}
        message['action'] = 'create'
        message['project_id'] = project_id
        message['body'] = service_json

        # send service_json to a queue
        # make sure to get ack
        queue.enqueue(message)

        return

    def update(self, project_id, service_name, service_obj, service_json):
        # do basic sanity checks

        message = {}
        message['action'] = 'update'
        message['project_id'] = project_id
        message['service_name'] = service_name
        message['body'] = service_json

        # make sure to get ack
        queue.enqueue(message)

        return

    def delete(self, project_id, service_name):
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_name)
        except Exception:
            raise LookupError('Service %s does not exist' % service_name)

        message = {}
        message['action'] = 'delete'
        message['project_id'] = project_id
        message['service_name'] = service_name

        # send service_json to a queue
        # make sure to get ack
        queue.enqueue(message)

        return
