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
try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp   # pragma: no cover

from oslo.config import cfg

from poppy import bootstrap
from poppy.distributed_task.taskflow.flow import akamai_create_san_cert
from poppy.distributed_task.taskflow.flow import akamai_mod_san_cert
from poppy.distributed_task.taskflow.flow import akamai_papi_jobs
from poppy.distributed_task.taskflow.flow import akamai_status_check
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


FLOW_MAPPING = {
    'CREATE-SAN-CERT': akamai_create_san_cert,
    'MOD-SAN-CERT': akamai_papi_jobs,
    'PAPI-JOBS': akamai_mod_san_cert,
    'STATUS-CHECK-AND-UPDATE': akamai_status_check
}


def run():
    conf = cfg.CONF
    conf(project='poppy', prog='poppy', args=[])

    b = bootstrap.Bootstrap(conf)
    # make sure enough argument is provided
    if len(sys.argv) < 2:
        print("Usage: %s <task_flow_name you want run>" % sys.argv[0])
        sys.exit(0)
    if sys.argv[1] not in FLOW_MAPPING.keys():
        raise ValueError(
            u'Flow name {0} in valid. Valid options are: {1}'.format(
                sys.argv[1],
                str(FLOW_MAPPING.keys())))

    kwargs = {}
    if sys.argv[1] == 'CREATE-SAN-CERT':
        if len(sys.argv) != 3:
            print("Usage: %s CREATE-SAN-CERT <path-to-san-cert-info-file>" %
                  sys.argv[0])
            sys.exit(0)
        else:
            cert_config = cp.ConfigParser()
            cert_config.read(sys.argv[2])
            kwargs = {
                'san_cert_creation_info_dict':
                    cert_config._sections['SAN-CERT-INFO']
            }
    elif len(sys.argv) != 2:
            print("Usage: %s <task_flow_name you want run>" % sys.argv[0])
            sys.exit(0)

    b.distributed_task.services_controller.submit_task(
        FLOW_MAPPING[sys.argv[1]].create_flow, **kwargs)
