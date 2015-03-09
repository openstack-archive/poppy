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

from oslo.utils import uuidutils
from taskflow.conductors import single_threaded
from taskflow import engines
from taskflow.persistence import logbook

from poppy.distributed_task import base
from poppy.openstack.common import log


LOG = log.getLogger(__name__)


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.driver = driver
        self.jobboard_backend_conf = self.driver.jobboard_backend_conf
        self.san_cert_add_job_backend = self.driver.san_cert_add_job_backend
        self.san_cert_remove_job_backend = (
            self.driver.san_cert_remove_job_backend)

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

    def run_task_worker(self):
        """Run a task flow worker (conductor).

        """
        with self.persistence as persistence:

            with self.driver.job_board(
                    self.jobboard_backend_conf.copy(),
                    persistence=persistence) as board:

                conductor = single_threaded.SingleThreadedConductor(
                    "Poppy service worker conductor", board, persistence,
                    engine='serial')

                conductor.run()

    def enqueue_add_san_cert_service(self, project_id, service_id):
        self.san_cert_add_job_backend.put(str.encode(json.dumps((
            project_id, service_id))))

    def enqueue_remove_san_cert_service(self, project_id, service_id):
        # We don't queu it up yet because currently there is no way
        # to remove a host from a san cert. Maybe we should just save
        # those hostnames to be deleted inside of a file
        # self.san_cert_remove_job_backend.put(str.encode(json.dumps((
        #     project_id, service_id))))
        pass

    def dequeue_all_add_san_cert_service(self):
        result = []
        for i in range(0, len(self.san_cert_add_job_backend)):
            i
            result.append(self.san_cert_add_job_backend.get())
            self.san_cert_add_job_backend.consume()
        return result

    def dequeue_all_remove_san_cert_service(self):
        # result = []
        # for i in range(0, len(self.san_cert_remove_job_backend)):
        #     i
        #     result.append(self.san_cert_remove_job_backend.get())
        #     self.san_cert_remove_job_backend.consume()
        # return result
        pass

    def requeue_mod_san_cert_services(self, added_services, removed_services):
        # ignore removed_service for right now
        self.san_cert_add_job_backend.put_all(added_services)

    def enqueue_papi_update_job(self, j_type, message):
        valid_j_type = ['rule', 'hosts', 'origin-ssl-cert']
        if j_type not in valid_j_type:
            raise ValueError(
                u'Status {0} not in valid options: {1}'.format(
                    j_type,
                    valid_j_type))
        else:
            self.papi_job_update_job_backend.put(json.dumps({
                'j_type': j_type,
                'message': message}))

    def dequeue_all_papi_update_job(self, j_type, message):
        result = []
        for i in range(0, len(self.papi_job_update_job_backend)):
            i
            result.append(self.papi_job_update_job_backend.get())
            self.papi_job_update_job_backend.consume()
        return result

    def requeue_papi_update_jobs(self, papi_job_list):
        self.papi_job_update_job_backend.put_all(papi_job_list)

    def enqueue_status_polling_queue(self, key, action, service_id_list):
        value = {(key, action): service_id_list}
        self.ssl_cert_status_polling_backend.put(str.encode(json.dumps(value)))
