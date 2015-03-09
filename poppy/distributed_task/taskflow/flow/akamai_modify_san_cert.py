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

from taskflow.patterns import linear_flow

from poppy.distributed_task.taskflow.task import akamai_papi_work_tasks


def create_flow():
    # this is just for pep8
    PropertyActivateTask = akamai_papi_work_tasks.PropertyActivateTask
    flow = linear_flow.Flow('Akamai PAPI Work Batch Job flow',
                            akamai_papi_work_tasks.PropertyUpdateTask(),
                            linear_flow.Flow('Akamai PAPI Property Activate'
                                             ' Task', retry=5).add(
                                PropertyActivateTask(
                                    requires=['update_version'])))
    return flow
