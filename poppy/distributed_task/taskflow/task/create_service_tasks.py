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
import time

from oslo.config import cfg
from taskflow import task

from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.utils import exc_loader
from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import provider_details
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class CreateProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, providers_list_json, project_id, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        providers_list = json.loads(providers_list_json)
        try:
            service_obj = self.storage_controller.get(project_id, service_id)
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

    def execute(self, responders, retry_sleep_time):
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

                    if any([isinstance(exception_class(), exception) for
                            exception in dns._driver.retry_exceptions]):
                        LOG.info('Due to {0} Exception, '
                                 'Task {1} will '
                                 'be retried'.format(exception_class,
                                                     self.__class__))
                        raise exception_class(msg)

        return dns_responder

    def revert(self, responders, retry_sleep_time, **kwargs):
        if self.name in kwargs['flow_failures'].keys():
            LOG.info('Sleeping for {0} seconds and '
                     'retrying'.format(retry_sleep_time))
            time.sleep(retry_sleep_time)


class CreateLogDeliveryContainerTask(task.Task):
    default_provides = "log_responders"

    def execute(self, project_id, auth_token, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        try:
            service_obj = self.storage_controller.get(project_id, service_id)
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
                            error_message=error_msg,
                            error_class=error_class))
                else:
                    access_urls = dns_responder[provider_name]['access_urls']
                    if log_responders:
                        access_urls.append({'log_delivery': log_responders})
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            provider_service_id=responder[provider_name]['id'],
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
