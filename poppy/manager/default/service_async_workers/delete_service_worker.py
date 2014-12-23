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
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details
)

LOG = log.getLogger(__file__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def service_delete_worker(provider_details,
                          project_id, service_id):
    LOG.logger.setLevel(logging.INFO)
    bootstrap_obj = bootstrap.Bootstrap(conf)
    service_controller = bootstrap_obj.manager.services_controller
    provider_details = json.loads(provider_details)

    responders = []
    # try to delete all service from each provider presented
    # in provider_details
    for provider in provider_details:
        provider_details[provider] = (
            req_provider_details.load_from_json(provider_details[provider]))
        LOG.info('Starting to delete service from %s' % provider)
        responder = service_controller.provider_wrapper.delete(
            service_controller._driver.providers[provider.lower()],
            provider_details)
        responders.append(responder)
        LOG.info('Deleting service from %s complete...' % provider)

    # delete associated cname records from DNS
    dns_responder = service_controller.dns_controller.delete(provider_details)

    for responder in responders:
        provider_name = list(responder.items())[0][0]

        if 'error' in responder[provider_name]:
            LOG.info('Delete service from %s failed' % provider_name)
            LOG.info('Updating provider detail status of %s for %s' %
                     (provider_name, service_id))
            # stores the error info for debugging purposes.
            provider_details[provider_name].error_info = (
                responder[provider_name].get('error_info'))
        elif 'error' in dns_responder[provider_name]:
            LOG.info('Delete service from DNS failed')
            LOG.info('Updating provider detail status of %s for %s'.format(
                     (provider_name, service_id)))
            # stores the error info for debugging purposes.
            provider_details[provider_name].error_info = (
                dns_responder[provider_name].get('error_info'))
        else:
            # delete service successful, remove this provider detail record
            del provider_details[provider_name]

        service_controller.storage_controller._driver.connect()

    if provider_details != {}:
        # Store failed provider details with error infomation for further
        # action, maybe for debug and/or support.
        LOG.info('Delete failed for one or more providers'
                 'Updating poppy service provider details for %s' %
                 service_id)
        service_controller.storage_controller.update_provider_details(
            project_id,
            service_id,
            provider_details)

    # always delete from Poppy.  Provider Details will contain
    # any provider issues that may have occurred.
    LOG.info('Deleting poppy service %s from all providers successful'
             % service_id)
    service_controller.storage_controller.delete(project_id, service_id)
    service_controller.storage_controller._driver.close_connection()
    LOG.info('Deleting poppy service %s succeeded' % service_id)
    LOG.info('Delete service worker process %s complete...' %
             str(os.getpid()))


if __name__ == '__main__':
    bootstrap_obj = bootstrap.Bootstrap(conf)

    parser = argparse.ArgumentParser(description='Delete service async worker'
                                     ' script arg parser')

    parser.add_argument('provider_details', action="store")
    parser.add_argument('project_id', action="store")
    parser.add_argument('service_id', action="store")

    result = parser.parse_args()
    provider_details = result.provider_details
    project_id = result.project_id
    service_id = result.service_id
    service_delete_worker(provider_details, project_id, service_id)
