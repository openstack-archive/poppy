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


class DefaultServicesController(base.ServicesController):
    """Default Services Controller."""

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller
        self.dns_controller = self._driver.dns.services_controller

    def list(self, project_id, marker=None, limit=None):
        """list.

        :param project_id
        :param marker
        :param limit
        :return list
        """
        return self.storage_controller.list(project_id, marker, limit)

    def get(self, project_id, service_name):
        """get.

        :param project_id
        :param service_name
        :return controller
        """
        return self.storage_controller.get(project_id, service_name)

    def create(self, project_id, service_obj):
        """create.

        :param project_id
        :param service_obj
        :raises LoookupError, ValueError
        """
        try:
            flavor = self.flavor_controller.get(service_obj.flavor_ref)
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

        """
        create_service_worker.service_create_worker(
            providers,
            self,
            project_id,
            service_name, service_obj)
        """
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
        """update.

        :param project_id
        :param service_name
        :param service_obj
        """
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
        """delete.

        :param project_id
        :param service_name
        :raises LookupError
        """
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

        """
        delete_service_worker.service_delete_worker(
            provider_details,
            self,
            project_id,
            service_name)
        """
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
