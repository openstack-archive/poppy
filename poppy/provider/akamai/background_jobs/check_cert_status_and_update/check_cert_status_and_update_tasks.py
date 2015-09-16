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
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class GetCertInfoTask(task.Task):
    default_provides = "cert_info"

    def execute(self, domain_name, cert_type, flavor_id, project_id):
        super(GetCertInfoTask, self).__init__()
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        res = self.storage_controller.get_cert_by_domain(domain_name,
                                                         cert_type,
                                                         flavor_id, project_id)
        return json.dumps(res)


class CheckCertStatusTask(task.Task):

    def execute(self, cert_info):
        pass
