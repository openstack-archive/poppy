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

from poppy.distributed_task.taskflow.task import akamai_modify_san_cert_tasks


def create_flow():
    flow = linear_flow.Flow('Modify San Cert Batch Job flow',
                            akamai_modify_san_cert_tasks.PrepareMODSANCertTask(
                            ),
                            akamai_modify_san_cert_tasks.MODSANCertRequestTask(
                            ))
    return flow
