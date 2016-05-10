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

"""Unittests for TaskFlow distributed_task service_controller."""

import mock
from oslo_config import cfg

from poppy.distributed_task.taskflow import driver
from tests.unit import base


class TestServiceController(base.TestCase):

    def setUp(self):
        super(TestServiceController, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.distributed_task_driver = (
            driver.TaskFlowDistributedTaskDriver(self.conf))
        self.mock_persistence_n_board = mock.Mock()
        self.mock_persistence_n_board.__enter__ = mock.Mock()
        self.mock_persistence_n_board.__exit__ = mock.Mock()
        self.distributed_task_driver.persistence = mock.Mock()
        self.distributed_task_driver.persistence.return_value = (
            self.mock_persistence_n_board)
        self.distributed_task_driver.job_board = mock.Mock()
        self.distributed_task_driver.job_board.return_value = (
            self.mock_persistence_n_board.copy())
        self.distributed_task_driver.job_board.return_value.__enter__ = (
            mock.Mock()
        )
        self.distributed_task_driver.job_board.return_value.__exit__ = (
            mock.Mock()
        )

    def test_persistence(self):
        self.assertTrue(self.distributed_task_driver.persistence is not None)

    def test_submit_task(self):
        flow_factory = mock.MagicMock
        self.distributed_task_driver.services_controller.submit_task(
            flow_factory,
            **{})

        # save the job logbook
        self.mock_persistence_n_board.__enter__().\
            get_connection().save_logbook.assert_called()
        # post job to board
        self.mock_persistence_n_board.copy().__enter__().post.assert_called()

    def test_run_task_worker(self):
        self.distributed_task_driver.services_controller.run_task_worker(
            'poppy')
        self.distributed_task_driver.persistence.assert_called()
        self.distributed_task_driver.job_board.assert_called()
