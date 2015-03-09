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

import json

import mock
from oslo.config import cfg

# from poppy.distributed_task.taskflow.flow import akamai_modify_san_cert
from poppy.distributed_task.taskflow.task import akamai_create_san_cert_tasks
from tests.unit import base
from tests.unit.distributed_task.taskflow.flow import akamai_mocks


class TestCreateSanCertFlow(base.TestCase):

    def setUp(self):
        super(TestCreateSanCertFlow, self).setUp()
        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient'
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

        bootstrap_patcher = mock.patch(
            'poppy.bootstrap.Bootstrap',
            new=akamai_mocks.MockBootStrap
        )
        bootstrap_patcher.start()
        self.addCleanup(bootstrap_patcher.stop)

        self.create_san_cert_task = (
            akamai_create_san_cert_tasks.CreateSANCertTask()
        )

    def test_CreateSANCertTask(self):
        self.assertTrue(self.create_san_cert_task.sc is not None)
        self.create_san_cert_task.execute({})
        self.create_san_cert_task.sc.enqueue_status_check_queue.assert_called()
