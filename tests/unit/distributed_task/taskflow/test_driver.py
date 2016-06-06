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

"""Unittests for TaskFlow distributed_task driver implementation."""

import mock

from oslo_config import cfg

from poppy.distributed_task.taskflow import driver
from tests.unit import base


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.persistence_backends_patcher = mock.patch(
            'poppy.distributed_task.taskflow.driver.persistence_backends')
        self.persistence = self.persistence_backends_patcher.start()
        self.persistence.backend.return_value.__enter__ = mock.MagicMock()
        self.persistence.backend.return_value.__exit__ = mock.MagicMock()

        self.job_backends_patcher = mock.patch(
            'poppy.distributed_task.taskflow.driver.job_backends')
        self.job_board = self.job_backends_patcher.start()
        self.mock_board = mock.MagicMock()
        type(self.mock_board).connected = False
        self.job_board.backend.return_value.__enter__ = mock.MagicMock(
            return_value=self.mock_board
        )
        self.job_board.backend.return_value.__exit__ = mock.MagicMock()

        self.conf = cfg.ConfigOpts()
        self.distributed_task_driver = (
            driver.TaskFlowDistributedTaskDriver(self.conf))

        self.addCleanup(self.persistence_backends_patcher.stop)
        self.addCleanup(self.job_backends_patcher.stop)

    def test_init(self):
        self.assertIsNotNone(self.distributed_task_driver)

    def test_vendor_name(self):
        self.assertEqual('TaskFlow', self.distributed_task_driver.vendor_name)

    def test_persistence(self):
        self.assertIsNotNone(self.distributed_task_driver.persistence())

    def test_job_board(self):
        self.assertIsNotNone(
            self.distributed_task_driver.job_board(mock.Mock(), mock.Mock()))

    def test_is_alive_true(self):
        type(self.mock_board).connected = True
        self.assertEqual(True, self.distributed_task_driver.is_alive())

    def test_is_alive_false(self):
        self.assertEqual(False, self.distributed_task_driver.is_alive())

    def test_is_alive_exception(self):
        # NOTE(isaacm): when mocking nested context manager the mocked
        # exception side effect should be on the outer context
        self.persistence.backend.return_value.__exit__.side_effect = Exception(
            "Mock __exit__ : Something went wrong!")

        self.assertEqual(False, self.distributed_task_driver.is_alive())

    def test_service_controller(self):
        self.assertIsNotNone(self.distributed_task_driver.services_controller)
