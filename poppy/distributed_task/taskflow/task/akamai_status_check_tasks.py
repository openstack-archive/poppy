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

import json
import os

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class StatusCheckAndUpdateTask(task.Task):
    default_provides = "update_version"

    def __init__(self):
        super(StatusCheckAndUpdateTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai']
        self.akamai_conf = self.akamai_driver.akamai_conf

    def execute(self):
        #
        pass

    def revert(self):
        pass