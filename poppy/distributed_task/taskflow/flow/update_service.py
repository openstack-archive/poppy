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
import logging
import os
import sys

from oslo.config import cfg
from taskflow.patterns import linear_flow
from taskflow import task

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import service


logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)

LOG = logging.getLogger('Poppy Service Tasks')
LOG.setLevel(logging.DEBUG)


conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def service_update_task_func(project_id, service_id,
                             service_old, service_obj):
    bootstrap_obj = bootstrap.Bootstrap(conf)
    service_controller = bootstrap_obj.manager.services_controller

    service_old_json = json.loads(service_old)
    service_obj_json = json.loads(service_obj)

    service_old = service.load_from_json(service_old_json)
    service_obj = service.load_from_json(service_obj_json)

    # save old provider details
    old_provider_details = service_old.provider_details

    responders = []
    # update service with each provider present in provider_details
    for provider in service_old.provider_details:
        LOG.info(u'Starting to update service from {0}'.format(provider))
        responder = service_controller.provider_wrapper.update(
            service_controller._driver.providers[provider.lower()],
            service_old.provider_details, service_obj)
        responders.append(responder)
        LOG.info(u'Updating service from {0} complete'.format(provider))

    # create dns mapping
    dns = service_controller.dns_controller
    dns_responder = dns.update(service_old, service_obj, responders)

    # gather links and status for service from providers
    error_flag = False
    provider_details_dict = {}

    for responder in responders:
        for provider_name in responder:
            if 'error' in responder[provider_name]:
                error_flag = True
                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        status='failed',
                        error_message=responder[provider_name]['error'],
                        error_info=responder[provider_name]['error_detail']))
            elif 'error' in dns_responder[provider_name]:
                error_flag = True
                error_msg = dns_responder[provider_name]['error']
                error_info = dns_responder[provider_name]['error_detail']

                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        error_info=error_info,
                        status='failed',
                        error_message=error_msg))
            else:
                access_urls = dns_responder[provider_name]['access_urls']

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

    if error_flag:
        # update the old provider details with errors
        for provider_name in provider_details_dict:
            error_info = provider_details_dict[provider_name].error_info
            error_message = provider_details_dict[provider_name].error_message
            old_provider_details[provider_name].error_info = error_info
            old_provider_details[provider_name].error_message = error_message
            old_provider_details[provider_name].status = 'failed'
        service_obj.provider_details = old_provider_details
    else:
        # update the provider details
        service_obj.provider_details = provider_details_dict

    # update the service object
    service_controller.storage_controller.update(project_id, service_id,
                                                 service_obj)

    service_controller.storage_controller._driver.close_connection()
    LOG.info('Update service worker process %s complete...' %
             str(os.getpid()))


class UpdateServiceTask(task.Task):
    default_provides = "service_updated"

    def execute(self, project_id, service_id, service_old, service_obj):
        LOG.info('Start executing update service task...')
        service_update_task_func(
            project_id, service_id,
            service_old, service_obj)
        return True


def update_service():
    flow = linear_flow.Flow('Updating poppy-service').add(
        UpdateServiceTask(),
    )
    return flow
