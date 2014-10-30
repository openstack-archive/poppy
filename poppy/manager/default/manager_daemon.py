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

from oslo.config import cfg

from poppy import bootstrap
#from poppy.manager.default import service_queue_workers
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import service
from poppy.openstack.common import log


LOG = log.getLogger(__name__)

def create_service_worker(mgr, project_id, service_name, service_obj):
    try:
        flavor = mgr.flavors_controller.get(service_obj.flavorRef)
    # raise a lookup error if the flavor is not found
    except LookupError as e:
        raise e

    providers_list = [p.provider_id for p in flavor.providers]
    service_name = service_obj.name

    responders = []
    # try to create all service from each provider
    services_controller = mgr.services_controller
    for provider in providers_list:
        responder = services_controller.provider_wrapper.create(
            services_controller._driver.providers[provider],
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

    services_controller.storage_controller.update_provider_details(
        project_id,
        service_name,
        provider_details_dict)

def manager_daemon(mgr):
    while True:
        message_body = mgr.queue.peek()
        if message_body is not None:
            print message_body
            print message_body.body
            message = message_body.body
            project_id = message['project_id']
            service_json = message['body']
            if message['action'] == 'create':
                service_name = service_json['name']
                service_obj = service.load_from_json(service_json)
                LOG.info('Starting to create service %s for %s' %
                         (service_name, project_id))
                create_service_worker(mgr, project_id,
                                            service_name,
                                            service_obj)
                mgr.queue.dequeue(message_body)
            else:
                LOG.info('Other actions (update/delete) does not have'
                         'worker implmented yet...')
            
if __name__ == '__main__':
    conf = cfg.CONF
    conf(project='poppy', prog='poppy', args=[])
    
    mgr = bootstrap.Bootstrap(conf).manager
    manager_daemon(mgr)
