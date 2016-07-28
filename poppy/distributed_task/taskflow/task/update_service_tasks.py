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

from __future__ import division

import json
import time

from oslo_config import cfg
from oslo_context import context as context_utils
from oslo_log import log
from taskflow import task

from poppy.distributed_task.taskflow.flow import delete_ssl_certificate
from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.utils import exc_loader
from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

DNS_OPTIONS = [
    cfg.IntOpt('retries', default=5,
               help='Total number of Retries after Exponentially Backing Off')
]

DNS_GROUP = 'driver:dns'

conf.register_opts(DNS_OPTIONS, group=DNS_GROUP)


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

    def execute(self, responders, retry_sleep_time,
                service_old, service_obj, project_id, service_id):
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

                        if any([exception_class == exception for
                                exception in dns._driver.retry_exceptions]):
                            LOG.info('Due to {0} Exception, '
                                     'Task {1} will '
                                     'be retried'.format(exception_class,
                                                         self.__class__))
                            raise exception_class(msg)
                else:
                    LOG.info("DNS Update Successful "
                             "for Provider {0} : "
                             "{1}".format(provider_name,
                                          dns_responder[provider_name]))
            except KeyError:
                # NOTE(TheSriram): This means the provider updates failed, and
                # just access_urls were returned
                pass

        return dns_responder

    def revert(self, responders, retry_sleep_time,
               service_old, service_obj,
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
                service_obj_json = json.loads(service_obj)
                service_obj = service.load_from_json(service_obj_json)

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
                domains_certificate_status = responder[provider_name].get(
                    'domains_certificate_status', {})
                if 'error' in responder[provider_name]:
                    error_flag = True
                    provider_details_dict[provider_name] = (
                        provider_details.ProviderDetail(
                            status='failed',
                            domains_certificate_status=(
                                domains_certificate_status),
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
                            domains_certificate_status=(
                                domains_certificate_status),
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

        self.storage_controller.update_service(
            project_id,
            service_id,
            service_obj
        )

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

            for domain in service_obj.domains:
                if hasattr(domain, 'cert_info'):
                    # we don't want store cert_info in database
                    # just generate it on demand
                    delattr(domain, 'cert_info')

        # update the service object
        LOG.info("Service to be updated to {0} "
                 "for project_id: {1} "
                 "and service_id: {2}".format(service_obj.to_dict(),
                                              project_id,
                                              service_id))
        self.storage_controller.update_service(
            project_id,
            service_id,
            service_obj
        )
        LOG.info('Update provider detail service worker process complete...')

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class DeleteCertsForRemovedDomains(task.Task):
    """Delete certificates domains deleted during service update."""

    def execute(self, service_old, service_obj, project_id):
        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        # get old domains
        service_old_json = json.loads(service_old)
        service_old = service.load_from_json(service_old_json)
        old_domains = set([
            domain.domain for domain in service_old.domains
            if domain.protocol == 'https' and domain.certificate == 'san'
        ])

        # get new domains
        service_new_json = json.loads(service_obj)
        service_new = service.load_from_json(service_new_json)
        new_domains = set([
            domain.domain for domain in service_new.domains
            if domain.protocol == 'https' and domain.certificate == 'san'
        ])

        removed_domains = old_domains.difference(new_domains)

        LOG.info("update_service Old domains: {0}".format(old_domains))
        LOG.info("update_service New domains: {0}".format(new_domains))
        LOG.info("update_service Deleted domains: {0}".format(removed_domains))

        kwargs = {
            'project_id': project_id,
            'cert_type': 'san',
            'context_dict': context_utils.get_current().to_dict()
        }

        for domain in removed_domains:
            kwargs['domain_name'] = domain
            LOG.info(
                "update_service removing certificate "
                "for deleted domain {0}".format(domain)
            )
            service_controller.distributed_task_controller.submit_task(
                delete_ssl_certificate.delete_ssl_certificate,
                **kwargs
            )
