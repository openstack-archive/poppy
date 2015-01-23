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

import contextlib
import logging

from oslo.utils import uuidutils
from taskflow import engines
from taskflow.persistence import logbook

from poppy.distributed_task import base


LOG = logging.getLogger(__name__)


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.driver = driver
        self.jobboard_backend_conf = self.driver.jobboard_backend_conf

    @property
    def persistence(self):
        return self.driver.persistence()

    def submit_task(self, flow_factory, **kwargs):
        """submit a task .

        """
        with self.persistence as persistence:

            with self.driver.job_board(
                self.jobboard_backend_conf.copy(), persistence=persistence) \
                    as board:

                    job_name = flow_factory.__name__
                    job_logbook = logbook.LogBook(job_name)
                    flow_detail = logbook.FlowDetail(job_name,
                                                     uuidutils.generate_uuid())
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
                    LOG.info("%s posted" % (job))
