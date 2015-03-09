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
import sys

from oslo.config import cfg

from poppy import bootstrap
from poppy.openstack.common import log
from poppy.distributed_task.taskflow.flow import akamai_modify_san_cert
from poppy.distributed_task.taskflow.flow import akamai_papi_work_flow

LOG = log.getLogger(__name__)


FLOW_MAPPING = {
    'MOD-SAN-CERT': akamai_modify_san_cert,
    'PAPI-JOBS': akamai_papi_work_flow
}


def run():
    conf = cfg.CONF
    conf(project='poppy', prog='poppy', args=[])

    b = bootstrap.Bootstrap(conf)
    if len(sys.argv) != 2:
        print("Usage: sys.argv[0] <task_flow_name you want run>")
        sys.exit(0)
    if sys.argv[1] not in FLOW_MAPPING.keys():
        raise ValueError(
            u'Flow name {0} in valid. Valid options are: {1}'.format(
                sys.argv[1],
                str(FLOW_MAPPING.keys())))
    b
    print FLOW_MAPPING[sys.argv[1]]
    # b.distributed_task.services_controller.submit_task(
    #     FLOW_MAPPING[sys.argv[1]])
