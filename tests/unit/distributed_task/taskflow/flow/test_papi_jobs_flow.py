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

"""Unittests for a specific TaskFlow flow: akamai_papi_jobs_tasks"""

import json

import mock
from oslo.config import cfg

# from poppy.distributed_task.taskflow.flow import akamai_papi_jobs_tasks
from poppy.distributed_task.taskflow.task import akamai_papi_jobs_tasks
from tests.unit import base
from tests.unit.distributed_task.taskflow.flow import akamai_mocks


hosts_message = [{"cnameTo": "secure.raxtest1.com.edgekey.net",
                  "cnameFrom": "www.blogyyy.com",
                  "edgeHostnameId": "ehn_1126816",
                  "cnameType": "EDGE_HOSTNAME"}, {
    "cnameTo": "secure.raxtest1.com.edgekey.net",
    "cnameFrom": "www.testxxx.com",
    "edgeHostnameId": "ehn_1126816",
    "cnameType": "EDGE_HOSTNAME"}]


class TestPapiWorkTaks(base.TestCase):

    def setUp(self):
        super(TestPapiWorkTaks, self).setUp()
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

        self.update_task = (
            akamai_papi_jobs_tasks.PropertyUpdateTask())

        self.activate_task = (
            akamai_papi_jobs_tasks.PropertyActivateTask())

    def test_PropertyUpdateTask_get_update_version(self):
        pass

    def test_PropertyUpdateTask(self):
        self.update_task.get_update_version = mock.Mock()
        self.update_task.get_update_version.return_value = 2
        result = self.update_task.execute()
        # This should return a tuple of version and service list
        self.assertTrue(len(result) == 2)

    def test_PropertyActivateTask(self):
        execute_param = (2, [
            {u'SPSStatusCheck': 1789},
            [u'["000", "f81f4459-ae02-4e3b-b36e-e4917adfe945"]',
             u'["000", "4fe3fbab-a73f-459d-be8a-74f9ff82c147"]']])
        self.activate_task.execute(execute_param)
        # ensure status check has been enqueued
        self.activate_task.sc.enqueue_status_check_queue.assert_called()

    def test_PropertyActivateTask_with_create_san_cert(self):
        execute_param = (2, [
            {u'SPSStatusCheck': 1789},
            [u'["secureEdgeHost", {"cnameHostname": "'
             'secure.san2.raxtest.com", '
             '"spsId": 1789, "jobID": 44434}]']])
        self.activate_task.execute(execute_param)
        # ensure status check has been enqueued
        self.activate_task.sc.enqueue_status_check_queue.assert_called()
