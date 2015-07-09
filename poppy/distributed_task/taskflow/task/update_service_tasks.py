# Copyright (c) 2015 Rackspace, Inc.
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
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class UpdateProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, service_old, service_obj):
        service_controller = memoized_controllers.task_controllers('poppy')

        service_old_json = json.loads(service_old)
        service_obj_json = json.loads(service_obj)

        service_old = service.load_from_json(service_old_json)
        service_obj = service.load_from_json(service_obj_json)

        responders = []
        # update service with each provider present in provider_details
        for provider in service_old.provider_details:
            LOG.info(u'Starting to update service from {0}'.format(provider))
            responder = service_controller.provider_wrapper.update(
                service_controller._driver.providers[provider.lower()],
                service_old.provider_details, service_obj)
            responders.append(responder)
            LOG.info(u'Updating service from {0} complete'.format(provider))

        return responders


class UpdateServiceDNSMappingTask(task.Task):
    default_provides = "dns_responder"

    def execute(self, responders, retry_sleep_time, service_old, service_obj):
        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)
        service_old_json = json.loads(service_old)
        service_old = service.load_from_json(service_old_json)
        dns_responder = dns.update(service_old, service_obj, responders)

        for provider_name in dns_responder:
            try:
                if 'error' in dns_responder[provider_name]:
                    msg = 'Update DNS for {0} ' \
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
            except KeyError:
                # NOTE(TheSriram): This means the provider updates failed, and
                # just access_urls were returned
                pass

        return dns_responder

    def revert(self, responders, retry_sleep_time, **kwargs):
        if self.name in kwargs['flow_failures'].keys():
            LOG.info('Sleeping for {0} seconds and '
                     'retrying'.format(retry_sleep_time))
            time.sleep(retry_sleep_time)


class UpdateLogDeliveryContainerTask(task.Task):
    default_provides = "log_responders"

    def execute(self, project_id, auth_token, service_old, service_obj):
        service_old_json = json.loads(service_old)
        service_obj_json = json.loads(service_obj)

        # check if log delivery is enabled in this PATCH
        if service_old_json['log_delivery']['enabled']:
            return
        if not service_obj_json['log_delivery']['enabled']:
            return

        log_responders = common.create_log_delivery_container(
            project_id, auth_token)

        return log_responders


class GatherProviderDetailsTask(task.Task):
    default_provides = "provider_details_dict_errors_tuple"

    def execute(self, responders, dns_responder, log_responders, project_id,
                service_id, service_obj):

        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)
        # gather links and status for service from providers
        error_flag = False
        error_class = None
        provider_details_dict = {}
        for responder in responders:
            for provider_name in responder:
                if 'error' in responder[provider_name]:
                    error_flag = True
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            status='failed',
                            error_message=responder[provider_name]['error'],
                            error_info=responder[provider_name]['error_detail']
                        ))
                elif 'error' in dns_responder[provider_name]:
                    error_flag = True
                    error_msg = dns_responder[provider_name]['error']
                    error_info = dns_responder[provider_name]['error_detail']
                    if 'error_class' in dns_responder[provider_name]:
                        # stores the error class for debugging purposes.
                        error_class = dns_responder[provider_name].get(
                            'error_class')
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            error_info=error_info,
                            status='failed',
                            error_message=error_msg,
                            error_class=error_class))
                else:
                    access_urls = dns_responder[provider_name]['access_urls']
                    if log_responders:
                        if not any('log_delivery' in access_url
                                   for access_url in access_urls):
                            access_urls.append({'log_delivery':
                                                log_responders})
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            provider_service_id=responder[provider_name]['id'],
                            access_urls=access_urls))
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

        self.storage_controller.update(project_id, service_id, service_obj)

        provider_details_dict_error_tuple = (provider_details_dict, error_flag)

        return provider_details_dict_error_tuple

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class UpdateProviderDetailsTask_Errors(task.Task):

    def execute(self, provider_details_dict_error_tuple, project_id,
                service_id, service_old, service_obj):

        (provider_details_dict, error_flag) = provider_details_dict_error_tuple
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_old_json = json.loads(service_old)
        service_old = service.load_from_json(service_old_json)
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)
        # de-serialize provider_details_dict
        provider_details_dict = dict([
            (k, provider_details.ProviderDetail.init_from_dict(detail))
            for k, detail
            in provider_details_dict.items()])

        # save old provider details
        old_provider_details = service_old.provider_details
        if error_flag:
            # update the old provider details with errors
            for provider_name in provider_details_dict:
                error_info = provider_details_dict[provider_name].error_info
                error_message = \
                    provider_details_dict[provider_name].error_message
                old_provider_details[provider_name].error_info = error_info
                old_provider_details[provider_name].error_message = \
                    error_message
                old_provider_details[provider_name].status = 'failed'
            service_obj.provider_details = old_provider_details

        else:
            # update the provider details
            service_obj.provider_details = provider_details_dict

        # update the service object
        self.storage_controller.update(project_id, service_id, service_obj)
        LOG.info('Update provider detail service worker process complete...')

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')
