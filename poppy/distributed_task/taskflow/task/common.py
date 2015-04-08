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

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details
)


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

LOG_DELIVERY_OPTIONS = [
    cfg.StrOpt('identity_url', default='',
               help='OpenStack Identity URL'),
    cfg.StrOpt('container_name', default='.CDN_ACCESS_LOGS',
               help='Swift container to put logs'),
    cfg.ListOpt('preferred_dcs', default=['DC1', 'DC2'],
                help='Preferred DCs to create container'),
]

LOG_DELIVERY_GROUP = 'log_delivery'


def create_log_delivery_container(project_id, auth_token):
    # log delivery enabled, create log delivery container for the user
    conf.register_opts(LOG_DELIVERY_OPTIONS, group=LOG_DELIVERY_GROUP)
    identity_url = conf['log_delivery']['identity_url']
    container_name = conf['log_delivery']['container_name']
    preferred_dcs = conf['log_delivery']['preferred_dcs']

    payload = {
        "auth": {
            "tenantName": project_id,
            "token": {
                "id": auth_token
            }
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(identity_url,
                                 data=json.dumps(payload),
                                 headers=headers)

        catalog = response.json()
        services = catalog['access']['serviceCatalog']
    except KeyError:
        LOG.info("Could not authenticate "
                 "with keystone : {0}".format(response.text))
        LOG.info("Skipping container {0} creation".format(container_name))
        return []

    swifturl_public = None
    swifturl_internal = None
    for service in services:

        if service['type'] == 'object-store':
            endpoints = service['endpoints']
            for endpoint in endpoints:
                if endpoint['region'] in preferred_dcs:
                    # TODO(obulpathi): Add both public and private urls.
                    # Only internal urls does not work because, not all
                    # containers are accessable from all DC's using
                    # internal urls
                    swifturl_public = endpoint['publicURL']
                    swifturl_internal = endpoint['internalURL']
                    break
    if swifturl_public and swifturl_internal:
        public_container_url = '{0}/{1}'.format(swifturl_public,
                                                container_name)
        internal_container_url = '{0}/{1}'.format(swifturl_internal,
                                                  container_name)
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': auth_token}
        LOG.info('Starting to '
                 'create container {0}'.format(public_container_url))
        response = requests.put(public_container_url,
                                None,
                                headers=headers)
        if response.ok:
            LOG.info('Created container {0}'.format(public_container_url))
            log_responders = [public_container_url, internal_container_url]
            return log_responders
        else:
            LOG.info('Error creating '
                     'container {0}'.format(public_container_url))
            return []
    else:
        return []


class UpdateProviderDetailTask(task.Task):

    def execute(self, provider_details_dict, project_id, service_id):
        provider_details_dict = dict([
            (k, provider_details.ProviderDetail.init_from_dict(detail))
            for k, detail
            in provider_details_dict.items()])
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        storage_controller = service_controller.storage_controller
        service_obj = storage_controller.get(project_id, service_id)
        service_obj.provider_details = provider_details_dict

        enabled = lambda provider: any([True if 'log_delivery'
                                        in access_url else False
                                        for access_url
                                        in provider.access_urls])

        if not all(map(enabled, provider_details_dict.values())):
            service_obj.log_delivery.enabled = False
        storage_controller.update(project_id, service_id, service_obj)

        storage_controller._driver.close_connection()
        LOG.info('Update service detail task complete...')


class UpdateProviderDetailIfNotEmptyTask(task.Task):
    default_provides = "provider_details_updated"

    def execute(self, changed_provider_details_dict, project_id, service_id):
        if changed_provider_details_dict != {}:
            provider_details_dict = dict([
                (k, provider_details.ProviderDetail.init_from_dict(detail))
                for k, detail
                in changed_provider_details_dict.items()])
            bootstrap_obj = bootstrap.Bootstrap(conf)
            service_controller = bootstrap_obj.manager.services_controller
            service_controller.storage_controller.update_provider_details(
                project_id,
                service_id,
                provider_details_dict)

            service_controller.storage_controller._driver.close_connection()
        LOG.info('Updating service detail task'
                 'complete for Changed Provider Details :'
                 '{0}'.format(changed_provider_details_dict))


class UpdateProviderDetailErrorTask(task.Task):
    default_provides = "changed_provider_details_dict"

    def execute(self, responders, service_id, provider_details):
        provider_details = json.loads(provider_details)
        for provider in provider_details:
            # NOTE(tonytan4ever): if the purge_url is None, it means to purge
            # all content, else only purge a specific purge url
            provider_details[provider] = (
                req_provider_details.load_from_json(
                    provider_details[provider]))

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
                LOG.info('Purging content from {0}'
                         'failed'.format(provider_name))
                LOG.info('Updating provider detail'
                         'status of {0} for {1}'.format(provider_name,
                                                        service_id))
                # stores the error info for debugging purposes.
                changed_provider_details_dict[provider_name] = (
                    provider_details[provider_name]
                )
                changed_provider_details_dict[provider_name].error_info = (
                    responder[provider_name].get('error_info')
                )

        # serialize changed_provider_details_dict
        for provider_name in changed_provider_details_dict:
            changed_provider_details_dict[provider_name] = (
                changed_provider_details_dict[provider_name].to_dict())

        return changed_provider_details_dict
