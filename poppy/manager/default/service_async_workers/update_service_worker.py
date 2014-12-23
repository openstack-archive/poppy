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

import argparse
import json
import logging
import os

from oslo.config import cfg

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import service

LOG = log.getLogger(__file__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def update_worker(project_id, service_id,
                  service_old, service_updates, service_obj):
    LOG.logger.setLevel(logging.INFO)
    bootstrap_obj = bootstrap.Bootstrap(conf)
    service_controller = bootstrap_obj.manager.services_controller

    service_old = service.load_from_json(json.loads(service_old))
    service_updates = service.load_from_json(json.loads(service_updates))
    service_obj = service.load_from_json(json.loads(service_obj))

    responders = []
    # update service with each provider present in provider_details
    for provider in service_old.provider_details:
        LOG.info(u'Starting to update service from {0}'.format(provider))
        responder = service_controller.provider_wrapper.update(
            service_controller._driver.providers[provider.lower()],
            service_old.provider_details, service_old, service_updates,
            service_obj)
        responders.append(responder)
        LOG.info(u'Updating service from {0} complete'.format(provider))

    # create dns mapping
    dns = service_controller.dns_controller
    dns_responder = dns.update(service_old, service_updates, responders)

    # gather links and status for service from providers
    provider_details_dict = {}
    for responder in responders:
        for provider_name in responder:
            if 'error' in responder[provider_name]:
                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        status='failed',
                        error_message=responder[provider_name]['error'],
                        error_info=responder[provider_name]['error_detail']))
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
                    provider_details_dict[provider_name].status = (
                        'deployed')

    # update the service object
    service_controller.storage_controller.update(project_id, service_id,
                                                 service_obj)
    # update the provider details
    service_controller.storage_controller.update_provider_details(
        project_id,
        service_id,
        provider_details_dict)

    service_controller.storage_controller._driver.close_connection()
    LOG.info('Update service worker process %s complete...' %
             str(os.getpid()))


if __name__ == '__main__':
    bootstrap_obj = bootstrap.Bootstrap(conf)

    parser = argparse.ArgumentParser(description='Delete service async worker'
                                     ' script arg parser')

    parser.add_argument('project_id', action="store")
    parser.add_argument('service_id', action="store")
    parser.add_argument('service_old', action="store")
    parser.add_argument('service_updates', action="store")
    parser.add_argument('service_obj', action="store")

    result = parser.parse_args()
    project_id = result.project_id
    service_id = result.service_id
    service_old = result.service_old
    service_updates = result.service_updates
    service_obj = result.service_obj
    update_worker(project_id, service_id, service_old, service_updates,
                  service_obj)
