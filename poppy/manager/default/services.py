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

from poppy.manager import base
from poppy.manager.default.service_async_workers import create_service_worker
from poppy.manager.default.service_async_workers import delete_service_worker
from poppy.manager.default.service_async_workers import purge_service_worker
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
        try:
            flavor = self.flavor_controller.get(service_obj.flavorRef)
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        providers = [p.provider_id for p in flavor.providers]
        service_name = service_obj.name

        try:
            self.storage_controller.create(
                project_id,
                service_obj)
        # ValueError will be raised if the service has already existed
        except ValueError as e:
            raise e

        self.storage_controller._driver.close_connection()
        p = multiprocessing.Process(
            name='Process: create poppy service %s for'
            ' project id: %s' %
            (service_name,
             project_id),
            target=create_service_worker.service_create_worker,
            args=(
                providers,
                self,
                project_id,
                service_name, service_obj))
        p.start()
        return

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
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_name)
        except Exception:
            raise LookupError('Service %s does not exist' % service_name)

        # change each provider detail's status to delete_in_progress
        # TODO(tonytan4ever): what if this provider is in 'failed' status?
        # Maybe raising a 400 error here ?
        for provider in provider_details:
            provider_details[provider].status = "delete_in_progress"

        self.storage_controller.update_provider_details(
            project_id,
            service_name,
            provider_details)

        self.storage_controller._driver.close_connection()
        p = multiprocessing.Process(
            name='Process: delete poppy service %s for'
            ' project id: %s' %
            (service_name,
             project_id),
            target=delete_service_worker.service_delete_worker,
            args=(
                provider_details,
                self,
                project_id,
                service_name))
        p.start()
        return

    def purge(self, project_id, service_name, purge_url=None):
        '''If purge_url is none, all content of this service will be purge.'''
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_name)
        except Exception:
            raise LookupError('Service %s does not exist' % service_name)

        # possible validation of purge url here...
        self.storage_controller._driver.close_connection()
        p = multiprocessing.Process(
            name='Process: Purge poppy service %s for'
            ' project id: %s'
            ' on %s' %
            (service_name,
             project_id,
             'all' if purge_url is None else purge_url),
            target=purge_service_worker.service_purge_worker,
            args=(
                provider_details,
                self,
                project_id,
                service_name,
                purge_url))
        p.start()
        return
