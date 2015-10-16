# Copyright (c) 2015 Rackspace, Inc.
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

from oslo_config import cfg
from oslo_log import log
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.transport.pecan.models.request import (
    provider_details as req_provider_details)
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class PurgeProviderServicesTask(task.Task):
    default_provides = "responders"

    def execute(self, service_obj, hard, provider_details, purge_url):
        service_controller = memoized_controllers.task_controllers('poppy')
        service_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_json)
        hard = json.loads(hard)
        provider_details = json.loads(provider_details)

        responders = []
        # try to purge all service from each provider presented
        # in provider_details
        for provider in provider_details:
            # NOTE(tonytan4ever): if the purge_url is None, it means to purge
            # all content, else only purge a specific purge url
            provider_details[provider] = (
                req_provider_details.load_from_json(
                    provider_details[provider]))

            LOG.info('Starting to purge service from {0},'
                     'purge_url: {1}'.format(provider,
                                             'all' if purge_url is None
                                             else purge_url))

            responder = service_controller.provider_wrapper.purge(
                service_controller._driver.providers[provider.lower()],
                service_obj,
                provider_details,
                hard=hard,
                purge_url=purge_url)
            responders.append(responder)

            LOG.info('Purge service {0}  on  {1} complete...'.format(
                     provider,
                     'all' if purge_url is None else purge_url))

        return responders
