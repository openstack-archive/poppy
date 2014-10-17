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


def service_purge_worker(provider_details, service_controller,
                         project_id, service_name, purge_url):
    responders = []
    # try to purge all service from each provider presented
    # in provider_details
    for provider in provider_details:
        # NOTE(tonytan4ever): if the purge_url is None, it means to purge
        # all content, else only purge a specific purge url
        LOG.info('Starting to purge service from %s, purge_url: %s' %
                 (provider,
                  'all' if purge_url is None else purge_url))
        responder = service_controller.provider_wrapper.purge(
            service_controller._driver.providers[provider.lower()],
            provider_details,
            purge_url)
        responders.append(responder)
        LOG.info('Purge service %s  on  %s complete...' %
                 (provider,
                  'all' if purge_url is None else purge_url))

    # Find any failed attempt of purging, and stores it in provider
    # detail for future debugging purpose
    changed_provider_details_dict = {}
    for responder in responders:
        # this is the item of responder, if there's "error"
        # key in it, it means the purging for this provider failed.
        # in that case we will need to update the provider detail
        # info for the service from poppy storage.
        provider_name = list(responder.items())[0][0]

        if 'error' in responder[provider_name]:
            LOG.info('Purging content from %s failed' % provider_name)
            LOG.info('Updating provider detail status of %s for %s' %
                     (provider_name, service_name))
            # stores the error info for debugging purposes.
            changed_provider_details_dict[provider_name] = (
                provider_details[provider_name]
            )
            changed_provider_details_dict[provider_name].error_info = (
                responder[provider_name].get('error_info')
            )

    # if there is an error for any puring attempts on a provider
    # record it in storage for further debugging purpose
    if not changed_provider_details_dict == {}:
        service_controller.storage_controller._driver.connect()
        provider_details.update(changed_provider_details_dict)
        service_controller.storage_controller.update_provider_details(
            project_id,
            service_name,
            provider_details)
