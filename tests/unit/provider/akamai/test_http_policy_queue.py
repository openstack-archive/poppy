# Copyright (c) 2016 Rackspace, Inc.
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

import mock
from oslo_config import cfg
from zake import fake_client

from poppy.provider.akamai.http_policy_queue import http_policy_queue
from tests.unit import base


AKAMAI_OPTIONS = [
    # queue backend configs
    cfg.StrOpt(
        'queue_backend_type',
        help='HTTP policy queueing backend'),
    cfg.ListOpt('queue_backend_host', default=['localhost'],
                help='default queue backend server hosts'),
    cfg.IntOpt('queue_backend_port', default=2181, help='default'
               ' default queue backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'http_policy_queue_path',
        default='/http_policy_queue',
        help='Zookeeper path '
        'for http_policy_queue'
    ),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class TestHTTPPolicyQueue(base.TestCase):

    def setUp(self):
        super(TestHTTPPolicyQueue, self).setUp()
        self.http_policy_dict = {
            "configuration_number": 1,
            "policy_name": "www.abc.com",
            "project_id": "12345"
        }

        # Need this fake class bc zake's fake client
        # does not take any host parameters
        class fake_kz_client(fake_client.FakeClient):
            def __init__(self, hosts):
                super(self.__class__, self).__init__()

        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient',
            fake_kz_client
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

        self.conf = cfg.ConfigOpts()
        self.zk_queue = http_policy_queue.ZookeeperHttpPolicyQueue(self.conf)

    def test_enqueue_http_policy(self):
        self.zk_queue.enqueue_http_policy(
            json.dumps(self.http_policy_dict).encode('utf-8'))
        self.assertTrue(len(self.zk_queue.http_policy_queue_backend) == 1)
        self.assertTrue(
            json.loads(self.zk_queue.http_policy_queue_backend.get().
                       decode('utf-8')) == self.http_policy_dict)

    def test_dequeue_http_policy(self):
        self.zk_queue.enqueue_http_policy(
            json.dumps(self.http_policy_dict).encode('utf-8'))
        res = self.zk_queue.dequeue_http_policy(False).decode('utf-8')
        self.assertTrue(len(self.zk_queue.http_policy_queue_backend) == 1)
        self.assertTrue(json.loads(res) == self.http_policy_dict)

        res = self.zk_queue.dequeue_http_policy().decode('utf-8')
        self.assertTrue(len(self.zk_queue.http_policy_queue_backend) == 0)
        self.assertTrue(json.loads(res) == self.http_policy_dict)

    def test_traverse_queue(self):
        self.zk_queue.enqueue_http_policy(
            json.dumps(self.http_policy_dict).encode('utf-8'))
        res = self.zk_queue.traverse_queue()
        self.assertTrue(len(res) == 1)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == [self.http_policy_dict])

    def test_traverse_queue_multiple_records(self):
        # Get a list of records to enqueue
        policy_obj_list = []
        for i in range(10):
            policy_object = {
                "configuration_number": 1,
                "policy_name": "www.abc{0}.com".format(i),
                "project_id": "12345{0}".format(i),
            }
            policy_obj_list.append(policy_object)

        for cert_obj in policy_obj_list:
            self.zk_queue.enqueue_http_policy(
                json.dumps(cert_obj).encode('utf-8'))
        res = self.zk_queue.traverse_queue()
        self.assertTrue(len(res) == 10)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == policy_obj_list)

    def test_put_queue_data(self):
        res = self.zk_queue.put_queue_data([])
        self.assertTrue(len(res) == 0)

        policy_obj_list = []
        for i in range(10):
            policy_object = {
                "configuration_number": 1,
                "policy_name": "www.abc{0}.com".format(i),
                "project_id": "12345{0}".format(i),
            }
            policy_obj_list.append(policy_object)

        self.zk_queue.put_queue_data(
            [json.dumps(o).encode('utf-8') for o in policy_obj_list])
        self.assertTrue(len(self.zk_queue.http_policy_queue_backend) == 10)
        res = self.zk_queue.traverse_queue()
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == policy_obj_list)

        # test put data to non-empty queue
        # should replace all items added above
        self.zk_queue.put_queue_data(
            [json.dumps(o).encode('utf-8') for o in policy_obj_list])
        self.assertTrue(len(self.zk_queue.http_policy_queue_backend) == 10)
