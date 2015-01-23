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


def service_create_task_func(providers_list_json,
                             project_id, service_id, service_obj_json):
    bootstrap_obj = bootstrap.Bootstrap(conf)
    service_controller = bootstrap_obj.manager.services_controller

    providers_list = json.loads(providers_list_json)
    service_obj = service.load_from_json(json.loads(service_obj_json))

    responders = []
    # try to create all service from each provider
    for provider in providers_list:
        LOG.info('Starting to create service from %s' % provider)
        responder = service_controller.provider_wrapper.create(
            service_controller._driver.providers[provider],
            service_obj)
        responders.append(responder)
        LOG.info('Create service from %s complete...' % provider)

    # create dns mapping
    dns = service_controller.dns_controller
    dns_responder = dns.create(responders)

    provider_details_dict = {}
    for responder in responders:
        for provider_name in responder:
            if 'error' in responder[provider_name]:
                error_msg = responder[provider_name]['error']
                error_info = responder[provider_name]['error_detail']

                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        error_info=error_info,
                        status='failed',
                        error_message=error_msg))
            elif 'error' in dns_responder[provider_name]:
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
                    provider_details_dict[provider_name].status = 'deployed'

    service_controller.storage_controller.update_provider_details(
        project_id,
        service_id,
        provider_details_dict)

    service_controller.storage_controller._driver.close_connection()
    LOG.info('Create service worker task complete...')


class CreateServiceTask(task.Task):
    default_provides = "service_created"

    def execute(self, providers_list_json,
                project_id, service_id, service_obj_json):
        LOG.info('Start executing create service task...')
        service_create_task_func(
            providers_list_json,
            project_id, service_id, service_obj_json)
        return True


def create_service():
    flow = linear_flow.Flow('Creating poppy-service').add(
        CreateServiceTask(),
    )
    return flow