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

from poppy.openstack.common import log

LOG = log.getLogger(__name__)


def service_delete_worker(provider_details, service_controller,
                          project_id, service_name):
    responders = []
    # try to delete all service from each provider presented
    # in provider_details
    for provider in provider_details:
        LOG.info('Starting to delete service from %s' % provider)
        responder = service_controller.provider_wrapper.delete(
            service_controller._driver.providers[provider.lower()],
            provider_details)
        responder = service_controller.dns_controller.delete(provider_details,
            responder)
        responders.append(responder)
        LOG.info('Deleting service from %s complete...' % provider)

    for responder in responders:
        # this is the item of responder, if there's "error"
        # key in it, it means the deletion for this provider failed.
        # in that case we cannot delete service from poppy storage.
        provider_name = list(responder.items())[0][0]

        if 'error' in responder[provider_name]:
            LOG.info('Delete service from %s failed' % provider_name)
            LOG.info('Updating provider detail status of %s for %s' %
                     (provider_name, service_name))
            # stores the error info for debugging purposes.
            provider_details[provider_name].error_info = (
                responder[provider_name].get('error_info')
            )
        else:
            # delete service successful, remove this provider detail record
            del provider_details[provider_name]

    service_controller.storage_controller._driver.connect()
    if provider_details == {}:
        # Only if all provider successfully deleted we can delete
        # the poppy service.
        LOG.info('Deleting poppy service %s from all providers successful'
                 % service_name)
        service_controller.storage_controller.delete(project_id, service_name)
        LOG.info('Deleting poppy service %s succeeded' % service_name)
    else:
        # Leave failed provider details with error infomation for further
        # action, maybe for debug and/or support.
        LOG.info('Updating poppy service provider details for %s' %
                 service_name)
        service_controller.storage_controller.update_provider_details(
            project_id,
            service_name,
            provider_details)
