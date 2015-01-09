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

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class UpdateProviderDetailTask(task.Task):
    default_provides = "provider_detail_updated"

    def execute(self, project_id, service_id,
                provider_details_dict):
        bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = bootstrap_obj.manager.services_controller
        service_controller.storage_controller.update_provider_details(
            project_id,
            service_id,
            provider_details_dict)
