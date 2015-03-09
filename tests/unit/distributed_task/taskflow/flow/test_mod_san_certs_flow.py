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

"""Unittests for a specific TaskFlow flow: akamai_modify_san_cert"""

import os

import mock

from poppy.distributed_task.taskflow.task import akamai_modify_san_cert_tasks
from tests.unit.distributed_task.taskflow.flow import akamai_mocks
from tests.unit.distributed_task.taskflow.flow import base


class TestModSanCertFlow(base.FlowTestBase):

    def setUp(self):
        super(TestModSanCertFlow, self).setUp()

        akamai_modify_san_cert_tasks.SAN_CERT_RECORDS_FILE_PATH = os.path.join(
            os.path.dirname(__file__),
            'test_SAN_certs.data')

        self.prepare_task = (
            akamai_modify_san_cert_tasks.PrepareMODSANCertTask())

        self.mod_san_request_task = (
            akamai_modify_san_cert_tasks.MODSANCertRequestTask())

    def test_PrepareMODSANCertTask(self):
        self.assertTrue(self.prepare_task.sc is not None)
        self.assertTrue(self.prepare_task.added_services ==
                        akamai_mocks.added_services_list)
        self.assertTrue(self.prepare_task.removed_services ==
                        akamai_mocks.removed_services_list)

        result = self.prepare_task.execute()
        # verify the result of execute
        self.assertTrue(result['added_services'] ==
                        akamai_mocks.added_services_list)
        self.assertTrue(result['removed_services'] ==
                        akamai_mocks.removed_services_list)
        print result['add.sans']
        self.assertTrue(result['add.sans'] == [u'www.blogyyy.com'])

    def test_MODSANCertRequestTask(self):
        self.assertTrue(self.mod_san_request_task.sc is not None)

        san_cert_mod_input = self.prepare_task.execute()
        self.mod_san_request_task._update_san_cert = mock.Mock()
        self.mod_san_request_task.execute(san_cert_mod_input)
        self.mod_san_request_task._update_san_cert.assert_called()
        self.mod_san_request_task.sc.enqueue_papi_update_job.assert_called()
