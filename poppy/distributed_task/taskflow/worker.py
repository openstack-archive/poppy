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

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow.conductors import single_threaded

logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)

LOG = logging.getLogger('taskflow')
LOG.setLevel(logging.DEBUG)


PERSISTENCE_BACKEND_CONF = {
    "connection": "zookeeper",
    "hosts": "192.168.59.103:2181"
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "hosts": "192.168.59.103:2181",
    "path": "/taskflow/jobs/poppy_service_worker_conduct",
}


def main():
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('poppy_service_worker_conduct',
                                  JOB_BACKEND_CONF.copy(),
                                  persistence=persistence) \
                as board:

            conductor = single_threaded.SingleThreadedConductor(
                "Poppy service worker conductor", board, persistence,
                engine='serial')

            conductor.run()


if __name__ == "__main__":
    sys.exit(main())