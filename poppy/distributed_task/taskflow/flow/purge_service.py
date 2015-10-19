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

from oslo_config import cfg
from oslo_log import log
from taskflow.patterns import linear_flow


from poppy.distributed_task.taskflow.task import common
from poppy.distributed_task.taskflow.task import purge_service_tasks


LOG = log.getLogger(__name__)


conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def purge_service():
    flow = linear_flow.Flow('Purging poppy-service').add(
        linear_flow.Flow('Update Oslo Context').add(
            common.ContextUpdateTask()),
        linear_flow.Flow('Purging Provider Services').add(
            purge_service_tasks.PurgeProviderServicesTask()),
        linear_flow.Flow('Purge provider details').add(
            common.UpdateProviderDetailErrorTask(
                rebind=['responders'])),
        common.UpdateProviderDetailIfNotEmptyTask(
            rebind=['changed_provider_details_dict']))
    return flow
