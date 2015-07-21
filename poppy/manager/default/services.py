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
from oslo_config import cfg

from poppy.common import errors
from poppy.distributed_task.taskflow.flow import create_service
from poppy.distributed_task.taskflow.flow import delete_service
from poppy.distributed_task.taskflow.flow import purge_service
from poppy.distributed_task.taskflow.flow import update_service
from poppy.distributed_task.taskflow.flow import update_service_state
from poppy.manager import base
from poppy.model.helpers import rule
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

    def determine_sleep_times(self):

        determined_sleep_time = \
            random.randrange(self.dns_conf.min_backoff_range,
                             self.dns_conf.max_backoff_range)

        backoff = [(2 ** i) * determined_sleep_time for i in
                   range(0, self.dns_conf.retries)]

        return backoff

    def _get_provider_details(self, project_id, service_id):
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_id)
        except Exception:
            raise LookupError(u'Service {0} does not exist'.format(
                service_id))
        return provider_details

    def get_service_by_domain_name(self, domain_name):
        try:
            service_details = self.storage_controller \
                                   .get_service_details_by_domain_name(
                                       domain_name)
        except Exception:
            raise LookupError(u'Domain {0} does not exist'.format(
                domain_name))
        return service_details

    def _append_defaults(self, service_json):
        # default origin rule
        for origin in service_json.get('origins', []):
            if origin.get('rules') is None:
                # add a rules section
                origin['rules'] = []

            if origin.get('rules') == []:
                # add the /* default request_url rule
                default_rule = rule.Rule(
                    name="default",
                    request_url='/*')
                origin['rules'].append(default_rule.to_dict())

        # default caching rule
        for caching_entry in service_json.get('caching', []):
            if caching_entry.get('rules') is None:
                # add a rules section
                caching_entry['rules'] = []

            if caching_entry.get('rules') == []:
                # add the /* default request_url rule
                default_rule = rule.Rule(
                    name="default",
                    request_url='/*')
                caching_entry['rules'].append(default_rule.to_dict())

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

    def create(self, project_id, auth_token, service_json):
        """create.

        :param project_id
        :param service_obj
        :raises LookupError, ValueError
        """

        try:
            flavor = self.flavor_controller.get(service_json.get('flavor_id'))
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        # add any default rules so its explicitly defined
        self._append_defaults(service_json)

        # convert to an object
        service_obj = service.Service.init_from_dict(service_json)
        service_id = service_obj.service_id

        # validate the service
        service_json = service_obj.to_dict()
        schema = service_schema.ServiceSchema.get_schema("service", "POST")
        validators.is_valid_service_configuration(service_json, schema)

        # deal with shared ssl domains
        for domain in service_obj.domains:
            if domain.protocol == 'https' and domain.certificate == 'shared':
                domain.domain = self._generate_shared_ssl_domain(
                    domain.domain
                )

        try:
            self.storage_controller.create(
                project_id,
                service_obj)
        # ValueError will be raised if the service has already existed
        except ValueError as e:
            raise e

        providers = [p.provider_id for p in flavor.providers]
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': project_id,
            'auth_token': auth_token,
            'service_id': service_id,
            'time_seconds': self.determine_sleep_times()
        }

        self.distributed_task_controller.submit_task(
            create_service.create_service, **kwargs)

        return service_obj

    def update(self, project_id, service_id, auth_token, service_updates):
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

        if service_old.operator_status == u'disabled':
            raise errors.ServiceStatusDisabled(
                u'Service {0} is disabled'.format(service_id))

        if service_old.status not in [u'deployed', u'failed']:
            raise errors.ServiceStatusNeitherDeployedNorFailed(
                u'Service {0} neither deployed nor failed'.format(service_id))

        # Fixing the operator_url domain for ssl
        # for schema validation
        existing_shared_domains = {}
        for domain in service_old.domains:
            if domain.protocol == 'https' and domain.certificate == 'shared':
                customer_domain = domain.domain.split('.')[0]
                existing_shared_domains[customer_domain] = domain.domain
                domain.domain = customer_domain

        service_old_json = json.loads(json.dumps(service_old.to_dict()))

        # remove fields that cannot be part of PATCH
        del service_old_json['service_id']
        del service_old_json['status']
        del service_old_json['operator_status']
        del service_old_json['provider_details']

        service_new_json = jsonpatch.apply_patch(
            service_old_json, service_updates)

        # add any default rules so its explicitly defined
        self._append_defaults(service_new_json)

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

        # check if the service domain names already exist
        for d in service_new.domains:
            if self.storage_controller.domain_exists_elsewhere(
                    d.domain,
                    service_id) is True:
                raise ValueError(
                    "Domain {0} has already been taken".format(d.domain))

        # fixing the old and new shared ssl domains in service_new
        for domain in service_new.domains:
            if domain.protocol == 'https' and domain.certificate == 'shared':
                customer_domain = domain.domain.split('.')[0]
                # if this domain is from service_old
                if customer_domain in existing_shared_domains:
                    domain.domain = existing_shared_domains[customer_domain]
                else:
                    domain.domain = self._generate_shared_ssl_domain(
                        domain.domain
                    )

        # set status in provider details to u'update_in_progress'
        provider_details = service_old.provider_details
        for provider in provider_details:
            provider_details[provider].status = u'update_in_progress'
        service_new.provider_details = provider_details
        self.storage_controller.update(project_id, service_id, service_new)

        kwargs = {
            'project_id': project_id,
            'service_id': service_id,
            'auth_token': auth_token,
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict()),
            'time_seconds': self.determine_sleep_times()
        }

        self.distributed_task_controller.submit_task(
            update_service.update_service, **kwargs)

        return

    def services_action(self, project_id, action):
        """find services of a .

        :param project_id
        :param state

        :raises ValueError
        """
        # list all the services of for this project_id
        # 10 per batch
        marker = None
        service_batch = self.storage_controller.list(project_id, marker, 10)
        while len(service_batch) > 0:
            marker = service_batch[-1].service_id
            # process previous batch
            for service_obj in service_batch:
                kwargs = {
                    'project_id': project_id,
                    'service_obj': json.dumps(service_obj.to_dict()),
                }
                try:
                    if action == 'delete':
                        LOG.info('Deleting  service: %s, project_id: %s' % (
                            service_obj.service_id, project_id))
                        self.delete(project_id, service_obj.service_id)
                    elif action == 'enable':
                        LOG.info('Enabling  service: %s, project_id: %s' % (
                            service_obj.service_id, project_id))
                        kwargs['state'] = 'enabled'
                        self.distributed_task_controller.submit_task(
                            update_service_state.enable_service, **kwargs)
                    elif action == 'disable':
                        LOG.info('Disabling  service: %s, project_id: %s' % (
                            service_obj.service_id, project_id))
                        kwargs['state'] = 'disabled'
                        self.distributed_task_controller.submit_task(
                            update_service_state.disable_service, **kwargs)
                except Exception as e:
                    # If one service's action failed, we log it and not
                    # impact other services' action
                    LOG.warning('Perform action %s on service: %s,'
                                ' project_id: %s failed, reason: %s' % (
                                    action,
                                    service_obj.service_id,
                                    project_id,
                                    str(e)))
            service_batch = self.storage_controller.list(project_id, marker,
                                                         10)

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
        try:
            service_obj = self.storage_controller.get(project_id, service_id)
        except ValueError as e:
            # This except is hit when service object does exist
            raise LookupError(str(e))

        if service_obj.status not in [u'deployed']:
            raise errors.ServiceStatusNotDeployed(
                u'Service {0} is not deployed.'.format(service_id))

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

    def _generate_shared_ssl_domain(self, domain_name):
        shared_ssl_domain_suffix = (
            self.dns_controller.generate_shared_ssl_domain_suffix())
        return '.'.join([domain_name, shared_ssl_domain_suffix])

    def migrate_domain(self, project_id, service_id, domain_name, new_cert):
        dns_controller = self.dns_controller
        storage_controller = self.storage_controller

        try:
            # Update CNAME records and provider_details in cassandra
            provider_details = storage_controller.get_provider_details(
                project_id, service_id)
        except ValueError as e:
            # If service is not found
            LOG.warning('Migrating domain failed: Service {0} could not '
                        'be found.. Error message: {1}'.format(service_id, e))
            raise errors.ServiceNotFound(e)

        for provider in provider_details:
            domain_found = False
            for url in provider_details[provider].access_urls:
                if url['domain'] == domain_name:
                    if 'operator_url' in url:
                        access_url = url['operator_url']
                        dns_controller.modify_cname(access_url, new_cert)
                        url['provider_url'] = new_cert
                        storage_controller.update_provider_details(
                            project_id,
                            service_id,
                            provider_details
                            )
                        domain_found = True
                        break
        if not domain_found:
            LOG.warning('Migrating domain failed: Domain {0} could not '
                        'be found.'.format(domain_name))
            raise LookupError('Domain {0} could not be found.'.format(
                domain_name))
