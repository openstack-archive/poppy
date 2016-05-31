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


from oslo_log import log
from oslo_utils import uuidutils
from taskflow.conductors.backends import impl_blocking
from taskflow import engines
from taskflow.listeners import logging as logging_listener
from taskflow.persistence import models
from taskflow.types.notifier import Notifier

from poppy.distributed_task import base


LOG = log.getLogger(__name__)


class NotifyingConductor(impl_blocking.BlockingConductor):

    def _listeners_from_job(self, job, engine):

        def task_transition(state, details):
            LOG.info("Taskflow transitioning to state {0}."
                     " Details: {1}".format(state, details))

        def flow_transition(state, details):
            LOG.info("Taskflow transitioning to state {0}."
                     " Details: {1}".format(state, details))

        engine.atom_notifier.register(Notifier.ANY, task_transition)
        engine.notifier.register(Notifier.ANY, flow_transition)

        listeners = super(NotifyingConductor,
                          self)._listeners_from_job(job, engine)

        listeners.append(logging_listener.LoggingListener(engine, log=LOG))
        return listeners


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.driver = driver
        self.jobboard_backend_conf = self.driver.jobboard_backend_conf

    @property
    def persistence(self):
        return self.driver.persistence()

    def submit_task(self, flow_factory, **kwargs):
        """submit a task.

        """
        with self.persistence as persistence:

            with self.driver.job_board(
                    self.jobboard_backend_conf.copy(),
                    persistence=persistence) as board:

                job_id = uuidutils.generate_uuid()
                job_name = '-'.join([flow_factory.__name__, job_id])
                job_logbook = models.LogBook(job_name)
                flow_detail = models.FlowDetail(
                    job_name, uuidutils.generate_uuid())
                factory_args = ()
                factory_kwargs = {}
                engines.save_factory_details(flow_detail, flow_factory,
                                             factory_args, factory_kwargs)
                job_logbook.add(flow_detail)
                persistence.get_connection().save_logbook(job_logbook)
                job_details = {
                    'store': kwargs
                }
                job = board.post(job_name,
                                 book=job_logbook,
                                 details=job_details)
                LOG.info("{0} posted".format(job))

    def run_task_worker(self, name):
        """Run a task flow worker (conductor).

        """
        with self.persistence as persistence:

            with self.driver.job_board(
                    self.jobboard_backend_conf.copy(),
                    persistence=persistence) as board:

                conductor = NotifyingConductor(
                    name, board, persistence,
                    engine='serial')

                conductor.run()
