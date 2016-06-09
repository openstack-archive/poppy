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

from oslo_config import cfg
from oslo_context import context as context_utils
from oslo_log import log
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details
)


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

DEFAULT_OPTIONS = [
    cfg.StrOpt('datacenter', default='',
               help='The datacenter in which poppy is deployed')
]

DEFAULT_GROUP = 'DEFAULT'

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
    conf.register_opts(DEFAULT_OPTIONS, group=DEFAULT_GROUP)
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
        LOG.info("Keystone request for {0}"
                 "finished "
                 "in {1} seconds".format(project_id,
                                         response.elapsed.total_seconds()))
        catalog = response.json()
        services = catalog['access']['serviceCatalog']
    except KeyError:
        LOG.info("Could not authenticate "
                 "with keystone : {0}".format(response.text))
        LOG.info("Skipping container {0} creation".format(container_name))
        return []

    swifturl_public = None
    swifturl_internal = None
    current_dc = None

    for service in services:

        if service['type'] == 'object-store':
            endpoints = service['endpoints']
            for endpoint in endpoints:
                if endpoint['region'] in preferred_dcs:
                    current_dc = endpoint['region']
                    swifturl_public = endpoint['publicURL']
                    swifturl_internal = endpoint['internalURL']
                    break

    if swifturl_public and swifturl_internal:
        public_container_url = '{0}/{1}'.format(swifturl_public,
                                                container_name)
        internal_container_url = '{0}/{1}'.format(swifturl_internal,
                                                  container_name)
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': auth_token
        }

        if conf['DEFAULT']['datacenter'].upper() == current_dc.upper():
            container_url = internal_container_url
            LOG.info("Choosing internalURL : {0}".format(container_url))
        else:
            container_url = public_container_url
            LOG.info("Choosing publicURL : {0}".format(container_url))

        LOG.info('Starting to '
                 'create container {0}'.format(container_url))
        response = requests.put(container_url,
                                headers=headers)
        LOG.info("Swift "
                 "request for {0} finished "
                 "in {1} seconds".format(project_id,
                                         response.elapsed.total_seconds()))
        LOG.info("Swift request's "
                 "response headers : {0}".format(str(response.headers)))
        if response.ok:
            LOG.info('Created container {0}'.format(container_url))

            container_urls = {
                'publicURL': public_container_url,
                'internalURL': internal_container_url
            }
            log_responders = [container_urls]
            return log_responders
        else:
            LOG.info('Error creating '
                     'container {0}'.format(container_url))
            return []
    else:
        return []


class ContextUpdateTask(task.Task):

    def execute(self, context_dict):
        context = context_utils.RequestContext.from_dict(context_dict)
        context.update_store()


class UpdateProviderDetailTask(task.Task):

    def execute(self, provider_details_dict, project_id, service_id):
        provider_details_dict = dict([
            (k, provider_details.ProviderDetail.init_from_dict(detail))
            for k, detail
            in provider_details_dict.items()])
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        service_obj = self.storage_controller.get_service(
            project_id,
            service_id
        )
        service_obj.provider_details = provider_details_dict

        enabled = lambda provider: any([True if 'log_delivery'
                                        in access_url else False
                                        for access_url
                                        in provider.access_urls])

        if not all(map(enabled, provider_details_dict.values())):
            service_obj.log_delivery.enabled = False
        LOG.info("Service to be updated to {0} "
                 "for project_id: {1} "
                 "and service_id: {2}".format(service_obj.to_dict(),
                                              project_id,
                                              service_id))
        self.storage_controller.update_service(
            project_id,
            service_id,
            service_obj
        )

        LOG.info('Update service detail task complete...')

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class UpdateProviderDetailIfNotEmptyTask(task.Task):
    default_provides = "provider_details_updated"

    def execute(self, changed_provider_details_dict, project_id, service_id):
        if changed_provider_details_dict != {}:
            provider_details_dict = dict([
                (k, provider_details.ProviderDetail.init_from_dict(detail))
                for k, detail
                in changed_provider_details_dict.items()])
            service_controller, self.storage_controller = \
                memoized_controllers.task_controllers('poppy', 'storage')
            self.storage_controller.update_provider_details(
                project_id,
                service_id,
                provider_details_dict)

        LOG.info("Provider Details to be updated to {0} "
                 "for project_id: {1} "
                 "and service_id: {2}".format(changed_provider_details_dict,
                                              project_id,
                                              service_id))

        LOG.info('Updating service detail task'
                 'complete for Changed Provider Details :'
                 '{0}'.format(changed_provider_details_dict))

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')


class UpdateProviderDetailErrorTask(task.Task):
    default_provides = "changed_provider_details_dict"

    def execute(self, responders, service_id, provider_details, hard):
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
                LOG.info('Purging content from {0} '
                         'failed'.format(provider_name))
                LOG.info('Updating provider detail '
                         'status of {0} for {1}'.format(provider_name,
                                                        service_id))
                # stores the error info for debugging purposes.
                changed_provider_details_dict[provider_name] = (
                    provider_details[provider_name]
                )
                changed_provider_details_dict[provider_name].error_info = (
                    responder[provider_name].get('error_detail')
                )
                changed_provider_details_dict[provider_name].error_message = (
                    responder[provider_name].get('error')
                )
                if not json.loads(hard):
                    changed_provider_details_dict[provider_name].status = \
                        'failed'
            else:
                changed_provider_details_dict[provider_name] = (
                    provider_details[provider_name]
                )
                changed_provider_details_dict[provider_name].status = (
                    'deployed')
                changed_provider_details_dict[provider_name].error_info = \
                    None
                changed_provider_details_dict[provider_name].error_message = \
                    None
        # serialize changed_provider_details_dict
        for provider_name in changed_provider_details_dict:
            changed_provider_details_dict[provider_name] = (
                changed_provider_details_dict[provider_name].to_dict())

        return changed_provider_details_dict
