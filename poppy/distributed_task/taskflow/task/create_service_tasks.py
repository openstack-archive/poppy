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

from __future__ import division

import json
import time

from oslo_config import cfg
from oslo_log import log
from taskflow import task

from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.utils import exc_loader
from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import provider_details


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

DNS_OPTIONS = [
    cfg.IntOpt('retries', default=5,
               help='Total number of Retries after Exponentially Backing Off')
]

DNS_GROUP = 'driver:dns'

conf.register_opts(DNS_OPTIONS, group=DNS_GROUP)


class CreateProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, providers_list_json, project_id, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        _, self.ssl_certificate_manager = \
            memoized_controllers.task_controllers('poppy', 'ssl_certificate')

        self.ssl_certificate_storage = self.ssl_certificate_manager.storage

        providers_list = json.loads(providers_list_json)
        try:
            service_obj = self.storage_controller.get_service(
                project_id,
                service_id
            )
            for domain in service_obj.domains:
                if domain.certificate == 'san':
                    cert_for_domain = (
                        self.ssl_certificate_storage.get_certs_by_domain(
                            domain.domain,
                            project_id=project_id,
                            flavor_id=service_obj.flavor_id,
                            cert_type=domain.certificate
                            ))
                    if cert_for_domain == []:
                        cert_for_domain = None
                    domain.cert_info = cert_for_domain
        except ValueError:
            msg = 'Creating service {0} from Poppy failed. ' \
                  'No such service exists'.format(service_id)
            LOG.info(msg)
            raise Exception(msg)

        responders = []
        # try to create all service from each provider
        for provider in providers_list:
            LOG.info('Starting to create service from {0}'.format(provider))
            responder = service_controller.provider_wrapper.create(
                service_controller._driver.providers[provider],
                service_obj)
            responders.append(responder)
            LOG.info('Create service from {0} complete...'.format(provider))

        return responders

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class CreateServiceDNSMappingTask(task.Task):
    default_provides = "dns_responder"

    def execute(self, responders, retry_sleep_time, project_id, service_id):
        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        dns_responder = dns.create(responders)
        for provider_name in dns_responder:
            if 'error' in dns_responder[provider_name]:
                msg = 'Create DNS for {0} ' \
                      'failed!'.format(provider_name)
                LOG.info(msg)
                if 'error_class' in dns_responder[provider_name]:
                    exception_repr = \
                        dns_responder[provider_name]['error_class']
                    exception_class = exc_loader(exception_repr)

                    if any([exception_class == exception for
                            exception in dns._driver.retry_exceptions]):
                        LOG.info('Due to {0} Exception, '
                                 'Task {1} will '
                                 'be retried'.format(exception_class,
                                                     self.__class__))
                        raise exception_class(msg)
            else:
                LOG.info("DNS Creation Successful "
                         "for Provider {0} : "
                         "{1}".format(provider_name,
                                      dns_responder[provider_name]))
        return dns_responder

    def revert(self, responders, retry_sleep_time,
               project_id, service_id, **kwargs):

        if self.name in kwargs['flow_failures'].keys():
            retries = conf[DNS_GROUP].retries
            current_progress = (1.0 / retries)
            if hasattr(self, 'retry_progress') \
                    and hasattr(self, 'retry_index'):
                self.retry_index = self.retry_index + 1
                self.retry_progress = current_progress * self.retry_index
            if not hasattr(self, 'retry_progress') \
                    and not hasattr(self, 'retry_index'):
                self.retry_progress = current_progress
                self.retry_index = 1
            if self.retry_progress == 1.0:
                LOG.warning(
                    'Maximum retry attempts of '
                    '{0} reached for Task {1}'.format(retries, self.name))
                LOG.warning(
                    'Setting of state of service_id: '
                    '{0} and project_id: {1} '
                    'to failed'.format(service_id, project_id))
                provider_details_dict = {}
                result = kwargs['result']

                service_controller, self.storage_controller = \
                    memoized_controllers.task_controllers('poppy', 'storage')

                try:
                    service_obj = self.storage_controller.get_service(
                        project_id,
                        service_id
                    )
                except ValueError:
                    msg = 'Creating service {0} from Poppy failed. ' \
                          'No such service exists'.format(service_id)
                    LOG.info(msg)
                    raise Exception(msg)

                for responder in responders:
                    for provider_name in responder:
                        provider_service_id = (
                            service_controller._driver.
                            providers[provider_name.lower()].obj.
                            service_controller.
                            get_provider_service_id(service_obj))
                        provider_details_dict[provider_name] = (
                            provider_details.ProviderDetail(
                                provider_service_id=provider_service_id,
                                error_info=result.traceback_str,
                                status='failed',
                                error_message='Failed after '
                                              '{0} DNS '
                                              'retries'.format(retries),
                                error_class=str(result.exc_info[0])))

                # serialize provider_details_dict
                for provider_name in provider_details_dict:
                    provider_details_dict[provider_name] = (
                        provider_details_dict[provider_name].to_dict())

                update_provider_details = common.UpdateProviderDetailTask()
                update_provider_details.execute(provider_details_dict,
                                                project_id,
                                                service_id)
            else:
                LOG.warning('Sleeping for {0} seconds and '
                            'retrying'.format(retry_sleep_time))
                if retry_sleep_time is not None:
                    time.sleep(retry_sleep_time)


class CreateLogDeliveryContainerTask(task.Task):
    default_provides = "log_responders"

    def execute(self, project_id, auth_token, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        try:
            service_obj = self.storage_controller.get_service(
                project_id,
                service_id
            )
            self.storage_controller._driver.close_connection()
        except ValueError:
            msg = 'Creating service {0} from Poppy failed. ' \
                  'No such service exists'.format(service_id)
            LOG.info(msg)
            raise Exception(msg)

        # if log delivery is not enabled, return
        if not service_obj.log_delivery.enabled:
            return []

        # log delivery enabled, create log delivery container for the user
        log_responders = common.create_log_delivery_container(
            project_id, auth_token)
        return log_responders

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class GatherProviderDetailsTask(task.Task):
    default_provides = "provider_details_dict"

    def execute(self, responders, dns_responder, log_responders):
        provider_details_dict = {}
        for responder in responders:
            for provider_name in responder:
                error_class = None
                domains_certificate_status = responder[provider_name].get(
                    'domains_certificate_status', {})
                if 'error' in responder[provider_name]:
                    error_msg = responder[provider_name]['error']
                    error_info = responder[provider_name]['error_detail']
                    if 'error_class' in responder[provider_name]:
                        error_class = \
                            responder[provider_name]['error_class']
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            error_info=error_info,
                            status='failed',
                            domains_certificate_status=(
                                domains_certificate_status),
                            error_message=error_msg,
                            error_class=error_class))
                elif 'error' in dns_responder[provider_name]:
                    error_msg = dns_responder[provider_name]['error']
                    error_info = dns_responder[provider_name]['error_detail']
                    if 'error_class' in dns_responder[provider_name]:
                        error_class = \
                            dns_responder[provider_name]['error_class']
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            error_info=error_info,
                            status='failed',
                            domains_certificate_status=(
                                domains_certificate_status),
                            error_message=error_msg,
                            error_class=error_class))
                else:
                    access_urls = dns_responder[provider_name]['access_urls']
                    if log_responders:
                        access_urls.append({'log_delivery': log_responders})
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            provider_service_id=responder[provider_name]['id'],
                            domains_certificate_status=(
                                domains_certificate_status),
                            access_urls=access_urls))

                    if 'status' in responder[provider_name]:
                        provider_details_dict[provider_name].status = (
                            responder[provider_name]['status'])
                    else:
                        provider_details_dict[provider_name].status = (
                            'deployed')

        # serialize provider_details_dict
        for provider_name in provider_details_dict:
            provider_details_dict[provider_name] = (
                provider_details_dict[provider_name].to_dict())

        return provider_details_dict
