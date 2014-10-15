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

from poppy.model.helpers import provider_details
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


def update_worker(service_controller, providers, project_id, service_name,
                  service_old, service_updates, service_obj):
    responders = []
    # update service with each provider present in provider_details
    for provider in service_old.provider_details:
        LOG.info(u'Starting to update service from {0}'.format(provider))
        responder = service_controller.provider_wrapper.update(
            service_controller._driver.providers[provider.lower()],
            service_old.provider_details, service_old, service_updates, service_obj)
        responders.append(responder)
        LOG.info(u'Updating service from {0} complete'.format(provider))

    """
    # check if any new providers are added to this flavor since the last time
    # the service has been created or updated
    new_providers = []
    for provider in providers:
        if provider not in provider_details:
            new_providers.append(provider)

    # create service with new providers for this flavor
    for provider in new_providers:
        responder = service_controller.provider_wrapper.create(
            service_controller._driver.providers[provider],
            service_obj)
        responders.append(responder)
    """

    import pdb; pdb.set_trace()
    # gather links and status for service from providers
    provider_details_dict = {}
    for responder in responders:
        for provider_name in responder:
            if 'error' not in responder[provider_name]:
                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        provider_service_id=responder[provider_name]['id'],
                        access_urls=[link['href'] for link in
                                     responder[provider_name]['links']])
                )
                if 'status' in responder[provider_name]:
                    provider_details_dict[provider_name].status = (
                        responder[provider_name]['status'])
                else:
                    provider_details_dict[provider_name].status = (
                        'deployed')
            else:
                provider_details_dict[provider_name] = (
                    provider_details.ProviderDetail(
                        error_info=responder[provider_name]['error_detail']))
                provider_details_dict[provider_name].status = 'failed'

    # update the status of service in storage
    service_controller.storage_controller.update_provider_details(
        project_id,
        service_name,
        provider_details_dict)
