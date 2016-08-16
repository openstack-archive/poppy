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

from oslo_config import cfg
from taskflow import engines
from taskflow.patterns import linear_flow

from oslo_log import log
from poppy.provider.akamai.background_jobs.update_property import (
    update_property_tasks)


LOG = log.getLogger(__name__)


conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def update_property_flow():
    flow = linear_flow.Flow('Update Akamai Property').add(
        update_property_tasks.PropertyGetLatestVersionTask(),
        update_property_tasks.PropertyUpdateTask(),
        update_property_tasks.PropertyActivateTask(),
        update_property_tasks.MarkQueueItemsWithActivatedProperty()
    )
    return flow


def run_update_property_flow(property_spec, update_type, update_info_list):
    e = engines.load(
        update_property_flow(),
        store={
            "property_spec": property_spec,
            "update_type": update_type,
            "update_info_list": update_info_list
        },
        engine='serial')
    e.run()
