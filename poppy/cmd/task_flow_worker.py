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

import os
import socket

from oslo_config import cfg
from oslo_log import log

from poppy import bootstrap


LOG = log.getLogger(__name__)


def run():
    conf = cfg.CONF
    log.register_options(conf)
    conf(project='poppy', prog='poppy')
    log.setup(conf, 'poppy')
    b = bootstrap.Bootstrap(conf)
    conductor_name = '{0}-{1}'.format(socket.gethostname(), os.getpid())
    b.distributed_task.services_controller.run_task_worker(name=conductor_name)
