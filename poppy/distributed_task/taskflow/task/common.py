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
import logging
import sys

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.model.helpers import provider_details
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details
)

logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)

LOG = logging.getLogger('Poppy Service Tasks')
LOG.setLevel(logging.DEBUG)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class UpdateProviderDetailTask(task.Task):

    def execute(self, provider_details_dict, project_id, service_id):
        provider_details_dict = dict([
            (k, provider_details.ProviderDetail.init_from_dict(detail))
            for k, detail
            in provider_details_dict.items()])
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        service_controller.storage_controller.update_provider_details(
            project_id,
            service_id,
            provider_details_dict)

        service_controller.storage_controller._driver.close_connection()
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
        LOG.info('Purging service detail task complete...')


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
                LOG.info('Purging content from %s failed' % provider_name)
                LOG.info('Updating provider detail status of %s for %s' %
                         (provider_name, service_id))
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
