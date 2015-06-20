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

from oslo.config import cfg
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class UpdateServiceStateTask(task.Task):
    def execute(self, project_id, service_obj, state):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        LOG.info(u'Starting to update service state to %s, for '
                 'project_id: %s, service_id: %s'
                 % (state, project_id, service_obj.service_id))
        self.storage_controller.update_state(
            project_id, service_obj.service_id, state)
        LOG.info(u'Update service state complete.')


class FixDNSChainTask(task.Task):
    def execute(self, service_obj):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        LOG.info(u'Starting to enable service')
        dns.enable(service_obj)
        LOG.info(u'Enabled service')

        return


class BreakDNSChainTask(task.Task):
    def execute(self, service_obj):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        LOG.info(u'Starting to disable service')
        dns.disable(service_obj)
        LOG.info(u'Disabled service')

        return
