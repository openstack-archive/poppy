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

import copy
import multiprocessing

from poppy.common import errors
from poppy.manager import base
from poppy.manager.default.service_async_workers import create_service_worker
from poppy.manager.default.service_async_workers import delete_service_worker
from poppy.manager.default.service_async_workers import purge_service_worker
from poppy.manager.default.service_async_workers import update_service_worker


class DefaultServicesController(base.ServicesController):
    """Default Services Controller."""

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller
        self.dns_controller = self._driver.dns.services_controller

    def _get_provider_details(self, project_id, service_name):
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_name)
        except Exception:
            raise LookupError(u'Service {0} does not exist'.format(
                service_name))
        return provider_details

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
            flavor = self.flavor_controller.get(service_obj.flavor_id)
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
        multiprocessing.active_children()
        p.start()
        return

    def update(self, project_id, service_name, service_updates):
        """update.

        :param project_id
        :param service_name
        :param service_updates
        """
        # get the current service object
        service_old = self.storage_controller.get(project_id, service_name)
        if service_old.status != u'deployed':
            raise errors.ServiceStatusNotDeployed(
                u'Service {0} not deployed'.format(service_name))

        service_obj = copy.deepcopy(service_old)

        # update service object
        if service_updates.name:
            raise Exception(u'Currently this operation is not supported')
        if service_updates.domains:
            service_obj.domains = service_updates.domains
        if service_updates.origins:
            service_obj.origins = service_updates.origins
        if service_updates.caching:
            raise Exception(u'Currently this operation is not supported')
        if service_updates.restrictions:
            raise Exception(u'Currently this operation is not supported')
        if service_updates.flavor_id:
            raise Exception(u'Currently this operation is not supported')

        # get provider details for this service
        provider_details = self._get_provider_details(project_id, service_name)

        # set status in provider details to u'update_in_progress'
        for provider in provider_details:
            provider_details[provider].status = u'update_in_progress'
        self.storage_controller.update_provider_details(
            project_id,
            service_name,
            provider_details)

        self.storage_controller._driver.close_connection()

        p = multiprocessing.Process(
            name=('Process: update poppy service {0} for project id: {1}'
                  .format(service_name, project_id)),
            target=update_service_worker.update_worker,
            args=(self, project_id, service_name, service_old, service_updates,
                  service_obj))
        multiprocessing.active_children()
        p.start()

        return

    def delete(self, project_id, service_name):
        """delete.

        :param project_id
        :param service_name
        :raises LookupError
        """
        provider_details = self._get_provider_details(project_id, service_name)

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
        multiprocessing.active_children()
        p.start()

        return

    def purge(self, project_id, service_name, purge_url=None):
        '''If purge_url is none, all content of this service will be purge.'''
        provider_details = self._get_provider_details(project_id, service_name)

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
        multiprocessing.active_children()
        p.start()
        return
