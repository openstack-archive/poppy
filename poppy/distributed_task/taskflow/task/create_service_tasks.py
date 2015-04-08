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
import requests
import time

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

LOG_DELIVERY_OPTIONS = [
    cfg.StrOpt('identity_url', default='http://identity.com',
               help='Identity URL for swiftfs container'),
    cfg.StrOpt('container_name', default='.CDN_ACCESS_LOGS',
               help='Swiftfs contailer to put logs'),
    cfg.StrOpt('preferred_dcs', default='DC1 DC2',
               help='Preferred DCs to create container'),
]

LOG_DELIVERY_GROUP = 'log_delivery'


class CreateProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, providers_list_json, project_id, service_id):
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        storage_controller = service_controller.storage_controller

        providers_list = json.loads(providers_list_json)
        try:
            service_obj = storage_controller.get(project_id, service_id)
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

        storage_controller._driver.close_connection()
        return responders


class CreateServiceDNSMappingTask(task.Task):
    default_provides = "dns_responder"

    def execute(self, responders, retry_sleep_time):
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        dns = service_controller.dns_controller
        dns_responder = dns.create(responders)
        for provider_name in dns_responder:
            if 'error' in dns_responder[provider_name]:
                if 'DNS Exception'\
                        in dns_responder[provider_name]['error']:
                    msg = 'Create DNS for {0} failed!'.format(provider_name)
                    LOG.info(msg)
                    raise Exception(msg)

        return dns_responder

    def revert(self, responders, retry_sleep_time, **kwargs):
        LOG.info('Sleeping for {0} seconds and '
                 'retrying'.format(retry_sleep_time))
        time.sleep(retry_sleep_time)


class CreateLogDeliveryContainerTask(task.Task):
    default_provides = "log_responders"

    def execute(self, project_id, auth_token, service_id):
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        storage_controller = service_controller.storage_controller

        conf.register_opts(LOG_DELIVERY_OPTIONS, group=LOG_DELIVERY_GROUP)
        identity_url = conf['log_delivery']['identity_url']
        container_name = conf['log_delivery']['container_name']
        preferred_dcs = conf['log_delivery']['preferred_dcs'].split()

        try:
            service_obj = storage_controller.get(project_id, service_id)
            storage_controller._driver.close_connection()
        except ValueError:
            msg = 'Creating service {0} from Poppy failed. ' \
                  'No such service exists'.format(service_id)
            LOG.info(msg)
            raise Exception(msg)


        log_responders = []
        # if log delivery is not enabled, return
        """
        if not service_obj.log_delivery:
            return log_responders
        """
        # log delivery enabled, create log delivery container for the user

        payload = {
            "auth": {
                "tenantName": project_id,
                "token": {
                    "id": auth_token
                }
            }
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(identity_url, data=json.dumps(payload), headers=headers)

        catalog = r.json()
        services = catalog['access']['serviceCatalog']

        for service in services:
            if service['name'] == 'cloudFiles':
                endpoints = service['endpoints']
                for endpoint in endpoints:
                    if endpoint['region'] in preferred_dcs:
                        swifturl = endpoint['publicURL']

        container_url = '{0}/{1}'.format(swifturl, container_name)
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': auth_token}
        LOG.info('Starting to create container {0}'.format(container_url))
        response = requests.put(container_url, None, headers=headers)
        LOG.info('Created container {0}'.format(container_url))
        log_responders = [container_url]
        return log_responders


class GatherProviderDetailsTask(task.Task):
    default_provides = "provider_details_dict"

    def execute(self, responders, dns_responder, log_responders):
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
                    access_urls.append({'log_delivery': log_responders[0]})
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
