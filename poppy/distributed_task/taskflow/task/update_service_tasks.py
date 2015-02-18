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

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy')


class UpdateProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, service_old, service_obj):
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller

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
        time.sleep(retry_sleep_time)
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        dns = service_controller.dns_controller
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)
        service_old_json = json.loads(service_old)
        service_old = service.load_from_json(service_old_json)
        dns_responder = dns.update(service_old, service_obj, responders)

        for provider_name in dns_responder:
            try:
                if 'error' in dns_responder[provider_name].keys():
                    if 'DNS Exception'\
                            in dns_responder[provider_name]['error_detail']:
                        msg = 'Update DNS for {0}' \
                              'failed!'.format(provider_name)
                        LOG.info(msg)
                        raise Exception(msg)
            except KeyError:
                # NOTE(TheSriram): This means the provider updates failed, and
                # just access_urls were returned
                pass

        return dns_responder

    def revert(self, responders, retry_sleep_time, **kwargs):
        LOG.info('Sleeping for {0} seconds and '
                 'retrying'.format(retry_sleep_time))


class GatherProviderDetailsTask(task.Task):
    default_provides = "provider_details_dict_errors_tuple"

    def execute(self, responders, dns_responder, project_id,
                service_id, service_obj):

        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)
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
                            error_info=responder[provider_name]['error_detail']
                        ))
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

        # serialize provider_details_dict
        for provider_name in provider_details_dict:
            provider_details_dict[provider_name] = (
                provider_details_dict[provider_name].to_dict())

        service_controller.storage_controller.update(project_id, service_id,
                                                     service_obj)

        provider_details_dict_error_tuple = (provider_details_dict, error_flag)

        return provider_details_dict_error_tuple


class UpdateProviderDetailsTask_Errors(task.Task):

    def execute(self, provider_details_dict_error_tuple, project_id,
                service_id, service_old, service_obj):

        (provider_details_dict, error_flag) = provider_details_dict_error_tuple
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
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
        service_controller.storage_controller.update(project_id, service_id,
                                                     service_obj)
        service_controller.storage_controller._driver.close_connection()
        LOG.info('Update provider detail service worker process complete...')
