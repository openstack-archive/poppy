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
from oslo_context import context as context_utils
from oslo_log import log
from taskflow import task

from poppy.distributed_task.taskflow.flow import delete_ssl_certificate
from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.utils import exc_loader
from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import provider_details as pd
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details
)

LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

DNS_OPTIONS = [
    cfg.IntOpt('retries', default=5,
               help='Total number of Retries after Exponentially Backing Off')
]

DNS_GROUP = 'driver:dns'

conf.register_opts(DNS_OPTIONS, group=DNS_GROUP)


class DeleteProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, provider_details, project_id):
        service_controller = memoized_controllers.task_controllers('poppy')
        provider_details = json.loads(provider_details)

        responders = []
        # try to delete all service from each provider presented
        # in provider_details
        for provider in provider_details:
            provider_details[provider] = (
                req_provider_details.load_from_json(provider_details[provider])
            )
            LOG.info('Starting to delete service from {0}'.format(provider))
            responder = service_controller.provider_wrapper.delete(
                service_controller._driver.providers[provider.lower()],
                provider_details,
                project_id)
            responders.append(responder)
            LOG.info('Deleting service from {0} complete...'.format(provider))
        return responders


class DeleteServiceDNSMappingTask(task.Task):
    default_provides = "dns_responder"

    def execute(self, provider_details, retry_sleep_time,
                responders, project_id, service_id):
        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        provider_details = json.loads(provider_details)
        for provider in provider_details:
            provider_details[provider] = (
                req_provider_details.load_from_json(provider_details[provider])
                )

        # delete associated cname records from DNS
        dns_responder = dns.delete(
            provider_details)
        for provider_name in dns_responder:
            if 'error' in dns_responder[provider_name]:
                msg = 'Delete DNS for {0} ' \
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
                LOG.info("DNS Deletion Successful "
                         "for Provider {0} : "
                         "{1}".format(provider_name,
                                      dns_responder[provider_name]))

        return dns_responder

    def revert(self, provider_details, retry_sleep_time,
               responders, project_id, service_id, **kwargs):
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
                for responder in responders:
                    for provider_name in responder:
                        provider_details_dict[provider_name] = (
                            pd.ProviderDetail(
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


class GatherProviderDetailsTask(task.Task):
    default_provides = "provider_details_dict"

    def execute(self, responders, dns_responder, provider_details):
        provider_details = json.loads(provider_details)
        for provider in provider_details:
            provider_details[provider] = (
                req_provider_details.load_from_json(provider_details[provider])
                )

        for responder in responders:
            provider_name = list(responder.items())[0][0]

            if 'error' in responder[provider_name]:
                LOG.info('Delete service from {0}'
                         'failed'.format(provider_name))
                # stores the error info for debugging purposes.
                provider_details[provider_name].error_info = (
                    responder[provider_name].get('error_info'))
            elif 'error' in dns_responder[provider_name]:
                LOG.info('Delete service from DNS failed')
                # stores the error info for debugging purposes.
                provider_details[provider_name].error_info = (
                    dns_responder[provider_name].get('error_info'))
                if 'error_class' in dns_responder[provider_name]:
                    # stores the error class for debugging purposes.
                    provider_details[provider_name].error_class = (
                        dns_responder[provider_name].get('error_class'))
            else:
                # delete service successful, remove this provider detail record
                del provider_details[provider_name]

        for provider in provider_details:
            provider_details[provider] = provider_details[provider].to_dict()

        return provider_details


class DeleteStorageServiceTask(task.Task):

    def execute(self, project_id, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        self.storage_controller.delete_service(project_id, service_id)

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class DeleteCertificatesForServiceSanDomains(task.Task):

    def execute(self, project_id, service_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        service_obj = self.storage_controller.get_service(
            project_id,
            service_id
        )

        kwargs = {
            'project_id': project_id,
            'cert_type': 'san',
            'context_dict': context_utils.get_current().to_dict()
        }

        for domain in service_obj.domains:
            if domain.protocol == 'https' and domain.certificate == 'san':
                kwargs["domain_name"] = domain.domain
                LOG.info(
                    "Delete service submit task san_cert deletion {0}".format(
                        domain.domain
                    )
                )
                service_controller.distributed_task_controller.submit_task(
                    delete_ssl_certificate.delete_ssl_certificate,
                    **kwargs
                )
