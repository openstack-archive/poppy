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


def create_service_worker(mgr, project_id, service_name, service_obj):
    try:
        flavor = mgr.flavor_controller.get(service_obj.flavorRef)
    # raise a lookup error if the flavor is not found
    except LookupError as e:
        raise e

    providers_list = [p.provider_id for p in flavor.providers]
    service_name = service_obj.name

    responders = []
    # try to create all service from each provider
    service_controller = mgr.service_controller
    for provider in providers_list:
        responder = service_controller.provider_wrapper.create(
            service_controller._driver.providers[provider],
            service_obj)
        responders.append(responder)

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
                        error_info=responder[provider_name]['error_detail']
                    )
                )
                provider_details_dict[provider_name].status = 'failed'

    service_controller.storage_controller.update_provider_details(
        project_id,
        service_name,
        provider_details_dict)