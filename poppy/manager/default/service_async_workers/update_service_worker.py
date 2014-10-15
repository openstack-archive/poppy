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


def update_worker(service_controller, project_id, service_name,
                  service_old, service_updates, service_obj):
    provider_details = service_old.provider_details
    responders = []
    # update service with each provider present in provider_details
    for provider in provider_details:
        LOG.info(u'Starting to update service from {0}'.format(provider))
        responder = service_controller.provider_wrapper.update(
            service_controller._driver.providers[provider.lower()],
            provider_details, service_old, service_updates, service_obj)
        responders.append(responder)
        LOG.info(u'Updating service from {0} complete'.format(provider))

    for responder in responders:
        # this is the item of responder, if there's "error"
        # key in it, it means update for this provider failed.
        # in that case we cannot delete service from poppy storage.
        provider_name = list(responder.items())[0][0]

        if 'error' in responder[provider_name]:
            LOG.info(u'Update service from {0} failed'.format(provider_name))
            LOG.info(u'Updating provider detail status of %s for %s' %
                     (provider_name, service_name))
            # stores the error info for debugging purposes.
            provider_details[provider_name].error_info = (
                responder[provider_name].get('error_detail'))
        else:
            # upding service successful, update the status of thsi provider
            provider_details[provider_name]

    # update the service details with provider
    service_controller.storage_controller.update_provider_details(
        project_id, service_name, provider_details)
