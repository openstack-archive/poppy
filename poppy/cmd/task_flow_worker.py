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

import logging
import sys

from oslo.config import cfg

from poppy import bootstrap

logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)

LOG = logging.getLogger('taskflow')
LOG.setLevel(logging.DEBUG)


if __name__ == "__main__":
    conf = cfg.CONF
    conf(project='poppy', prog='poppy', args=[])

    b = bootstrap.Bootstrap(conf)
    b.distributed_task.services_controller.run_task_worker()
