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

import logging
import sys

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.model.helpers import provider_details

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

    def execute(self, provider_details_dict, project_id, service_id):
        if provider_details_dict != {}:
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
