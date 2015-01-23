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

from oslo.config import cfg
from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends

from poppy.distributed_task import base
from poppy.distributed_task.taskflow import controllers


LOG = logging.getLogger(__name__)

TASKFLOW_OPTIONS = [
    cfg.StrOpt('jobboard_backend_type', default='zookeeper',
               help='Default jobboard backend type'),
    cfg.StrOpt('persistent_backend_type', default='zookeeper',
               help='Default jobboard persistent backend type'),
    cfg.StrOpt('jobboard_backend_host', default='localhost',
               help='default jobboard backend server host'),
    cfg.IntOpt('jobboard_backend_port', default=2181, help='default'
               ' jobboard backend server port (e.g: ampq)'),
    cfg.StrOpt('persistent_backend_host', default='localhost',
               help='default persistent backend server host'),
    cfg.IntOpt('persistent_backend_port', default=2181, help='default'
               ' default persistent backend server port (e.g: ampq)'),
]

TASKFLOW_GROUP = 'drivers:distributed_task:taskflow'


class TaskFlowDistributedTaskDriver(base.Driver):
    """TaskFlow distributed task Driver."""

    def __init__(self, conf):
        super(TaskFlowDistributedTaskDriver, self).__init__(conf)
        conf.register_opts(TASKFLOW_OPTIONS, group=TASKFLOW_GROUP)
        self.distributed_task_conf = conf[TASKFLOW_GROUP]
        self.jobboard_backend_conf = {
            # This topic could become more complicated
            "board": self.distributed_task_conf.jobboard_backend_type,
            "hosts": "%s:%s" % (
                self.distributed_task_conf.jobboard_backend_host,
                self.distributed_task_conf.jobboard_backend_port),
            "path": "/taskflow/jobs/poppy_service_worker_conduct",
        }

        self.persistence_backend_conf = {
            # This topic could become more complicated
            "connection": self.distributed_task_conf.persistent_backend_type,
            "hosts": "%s:%s" % (
                self.distributed_task_conf.persistent_backend_host,
                self.distributed_task_conf.persistent_backend_port),
        }

        self._persistence = None

    def is_alive(self):
        """Health check for TaskFlow worker."""
        return True

    def persistence(self):
        if self._persistence is None:
            self._persistence = persistence_backends.backend(
                self.persistence_backend_conf.copy())
        return self._persistence

    def job_board(self, conf, persistence, **kwargs):
        return job_backends.backend(
            'poppy_service_worker_conduct',
            conf.copy(), persistence=persistence)

    @property
    def vendor_name(self):
        """storage name.

        :returns 'TaskFlow'
        """
        return 'TaskFlow'

    @property
    def services_controller(self):
        """services_controller.

        :returns service controller
        """
        return controllers.ServicesController(self)
