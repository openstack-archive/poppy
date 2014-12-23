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
import json
import os
import subprocess

from poppy.common import errors
from poppy.manager import base
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


class DefaultServicesController(base.ServicesController):

    """Default Services Controller."""

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller
        self.dns_controller = self._driver.dns.services_controller

    def _get_provider_details(self, project_id, service_id):
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_id)
        except Exception:
            raise LookupError(u'Service {0} does not exist'.format(
                service_id))
        return provider_details

    def list(self, project_id, marker=None, limit=None):
        """list.

        :param project_id
        :param marker
        :param limit
        :return list
        """
        return self.storage_controller.list(project_id, marker, limit)

    def get(self, project_id, service_id):
        """get.

        :param project_id
        :param service_id
        :return controller
        """
        return self.storage_controller.get(project_id, service_id)

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
        service_id = service_obj.service_id

        try:
            self.storage_controller.create(
                project_id,
                service_obj)
        # ValueError will be raised if the service has already existed
        except ValueError as e:
            raise e

        proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'service_async_workers',
                                  'sub_process_proxy.py')
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'service_async_workers',
                                   'create_service_worker.py')
        cmd_list = ['python',
                    proxy_path,
                    script_path,
                    json.dumps(providers),
                    project_id, service_id,
                    json.dumps(service_obj.to_dict())]
        LOG.info('Starting create service subprocess: %s' % cmd_list)
        p = subprocess.Popen(cmd_list)
        p.communicate()

        return

    def update(self, project_id, service_id, service_updates):
        """update.

        :param project_id
        :param service_id
        :param service_updates
        """
        # get the current service object
        service_old = self.storage_controller.get(project_id, service_id)
        if service_old.status != u'deployed':
            raise errors.ServiceStatusNotDeployed(
                u'Service {0} not deployed'.format(service_id))

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
        provider_details = self._get_provider_details(project_id, service_id)

        # set status in provider details to u'update_in_progress'
        for provider in provider_details:
            provider_details[provider].status = u'update_in_progress'
        self.storage_controller.update_provider_details(
            project_id,
            service_id,
            provider_details)

        proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'service_async_workers',
                                  'sub_process_proxy.py')
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'service_async_workers',
                                   'update_service_worker.py')
        cmd_list = ['python',
                    proxy_path,
                    script_path,
                    project_id, service_id,
                    json.dumps(service_old.to_dict()),
                    json.dumps(service_updates.to_dict()),
                    json.dumps(service_obj.to_dict())]
        LOG.info('Starting update service subprocess: %s' % cmd_list)
        p = subprocess.Popen(cmd_list)
        p.communicate()

        return

    def delete(self, project_id, service_id):
        """delete.

        :param project_id
        :param service_id
        :raises LookupError
        """
        provider_details = self._get_provider_details(project_id, service_id)

        # change each provider detail's status to delete_in_progress
        # TODO(tonytan4ever): what if this provider is in 'failed' status?
        # Maybe raising a 400 error here ?
        for provider in provider_details:
            provider_details[provider].status = "delete_in_progress"

        self.storage_controller.update_provider_details(
            project_id,
            service_id,
            provider_details)

        proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'service_async_workers',
                                  'sub_process_proxy.py')
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'service_async_workers',
                                   'delete_service_worker.py')
        cmd_list = ["python",
                    proxy_path,
                    script_path,
                    json.dumps(dict([(k, v.to_dict())
                                     for k, v in provider_details.items()])),
                    project_id, service_id]
        LOG.info('Starting delete service subprocess: %s' % cmd_list)
        p = subprocess.Popen(cmd_list)
        p.communicate()

        return

    def purge(self, project_id, service_id, purge_url=None):
        '''If purge_url is none, all content of this service will be purge.'''
        provider_details = self._get_provider_details(project_id, service_id)

        # possible validation of purge url here...
        proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'service_async_workers',
                                  'sub_process_proxy.py')
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'service_async_workers',
                                   'purge_service_worker.py')
        cmd_list = ["python",
                    proxy_path,
                    script_path,
                    json.dumps(dict([(k, v.to_dict())
                                     for k, v in provider_details.items()])),
                    project_id, service_id,
                    str(purge_url)]

        LOG.info('Starting purge service subprocess: %s' % cmd_list)
        p = subprocess.Popen(cmd_list)
        p.communicate()

        return
