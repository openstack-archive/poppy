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

import json
import random

import jsonpatch
from oslo.config import cfg

from poppy.common import errors
from poppy.distributed_task.taskflow.flow import create_service
from poppy.distributed_task.taskflow.flow import delete_service
from poppy.distributed_task.taskflow.flow import purge_service
from poppy.distributed_task.taskflow.flow import update_service
from poppy.manager import base
from poppy.model import service
from poppy.openstack.common import log
from poppy.transport.validators import helpers as validators
from poppy.transport.validators.schemas import service as service_schema

LOG = log.getLogger(__name__)

DNS_OPTIONS = [
    cfg.IntOpt(
        'retries',
        default=5,
        help='Total number of Retries after Exponentially Backing Off'),
    cfg.IntOpt(
        'min_backoff_range',
        default=20,
        help='Minimum Number of seconds to sleep between retries'),
    cfg.IntOpt(
        'max_backoff_range',
        default=30,
        help='Maximum Number of seconds to sleep between retries'),
]

DNS_GROUP = 'drivers:dns'


class DefaultServicesController(base.ServicesController):

    """Default Services Controller."""

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller
        self.dns_controller = self._driver.dns.services_controller
        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller)

        self.driver.conf.register_opts(DNS_OPTIONS,
                                       group=DNS_GROUP)
        self.dns_conf = self.driver.conf[DNS_GROUP]
        self.default_sleep_time = [0]

    def determine_sleep_times(self):

        default_sleep_time = [0]
        determined_sleep_time = random.randrange(self.dns_conf.min_backoff_range,
                                                 self.dns_conf.max_backoff_range)

        backoff = [(2**i) * determined_sleep_time
                        for i in range(0, self.dns_conf.retries)]

        return default_sleep_time + backoff

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
        :raises LookupError, ValueError
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

        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': project_id,
            'service_id': service_id,
            'time_seconds': self.determine_sleep_times()
        }

        self.distributed_task_controller.submit_task(
            create_service.create_service, **kwargs)

        return

    def update(self, project_id, service_id, service_updates):
        """update.

        :param project_id
        :param service_id
        :param service_updates
        :raises LookupError, ValueError
        """
        # get the current service object
        try:
            service_old = self.storage_controller.get(project_id, service_id)
        except ValueError:
            raise errors.ServiceNotFound("Service not found")

        if service_old.status not in [u'deployed', u'failed']:
            raise errors.ServiceStatusNeitherDeployedNorFailed(
                u'Service {0} neither deployed nor failed'.format(service_id))

        service_old_json = json.loads(json.dumps(service_old.to_dict()))

        # remove fields that cannot be part of PATCH
        del service_old_json['service_id']
        del service_old_json['status']
        del service_old_json['provider_details']

        service_new_json = jsonpatch.apply_patch(
            service_old_json, service_updates)

        # validate the updates
        schema = service_schema.ServiceSchema.get_schema("service", "POST")
        validators.is_valid_service_configuration(service_new_json, schema)

        try:
            self.flavor_controller.get(service_new_json['flavor_id'])
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        # must be valid, carry on
        service_new_json['service_id'] = service_old.service_id
        service_new = service.Service.init_from_dict(service_new_json)

        # set status in provider details to u'update_in_progress'
        provider_details = service_old.provider_details
        for provider in provider_details:
            provider_details[provider].status = u'update_in_progress'
        self.storage_controller.update(project_id, service_id, service_old)

        kwargs = {
            'project_id': project_id,
            'service_id': service_id,
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict()),
            'time_seconds': self.determine_sleep_times()
        }

        self.distributed_task_controller.submit_task(
            update_service.update_service, **kwargs)

        return

    def delete(self, project_id, service_id):
        """delete.

        :param project_id
        :param service_id
        :raises LookupError
        """
        service_obj = self.storage_controller.get(project_id, service_id)

        # get provider details for this service
        provider_details = self._get_provider_details(project_id, service_id)

        # change each provider detail's status to delete_in_progress
        for provider in service_obj.provider_details:
            service_obj.provider_details[provider].status = (
                u'delete_in_progress')

        self.storage_controller.update(project_id, service_id, service_obj)

        kwargs = {
            "provider_details": json.dumps(
                dict([(k, v.to_dict()) for k, v in provider_details.items()])),
            "project_id": project_id,
            "service_id": service_id,
            'time_seconds': self.determine_sleep_times()
        }

        self.distributed_task_controller.submit_task(
            delete_service.delete_service, **kwargs)

        return

    def purge(self, project_id, service_id, purge_url=None):
        '''If purge_url is none, all content of this service will be purge.'''
        provider_details = self._get_provider_details(project_id, service_id)

        # possible validation of purge url here...
        kwargs = {
            'provider_details': json.dumps(
                dict([(k, v.to_dict()) for k, v in provider_details.items()])),
            'project_id': project_id,
            'service_id': service_id,
            'purge_url': str(purge_url)
        }

        self.distributed_task_controller.submit_task(
            purge_service.purge_service, **kwargs)

        return
