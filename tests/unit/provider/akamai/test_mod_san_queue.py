# Copyright (c) 2015 Rackspace, Inc.
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

import mock
from oslo_config import cfg

from poppy.provider.akamai.mod_san_queue import zookeeper_queue
from tests.unit import base


AKAMAI_OPTIONS = [
    # queue backend configs
    cfg.StrOpt(
        'queue_backend_type',
        help='SAN Cert Queueing backend'),
    cfg.ListOpt('queue_backend_host', default=['localhost'],
                help='default queue backend server hosts'),
    cfg.IntOpt('queue_backend_port', default=2181, help='default'
               ' default queue backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'mod_san_queue_path', default='/mod_san_queue', help='Zookeeper path '
        'for mod_san_queue'),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class TestModSanQueue(base.TestCase):

    def setUp(self):
        super(TestModSanQueue, self).setUp()
        self.cert_obj_json = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }
        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient'
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

        self.conf = cfg.ConfigOpts()
        self.zk_queue = zookeeper_queue.ZookeeperModSanQueue(self.conf)

        self.zk_queue.mod_san_queue_backend = mock.Mock()

    def test_enqueue_mod_san_request(self):
        self.zk_queue.enqueue_mod_san_request(self.cert_obj_json)
        self.zk_queue.mod_san_queue_backend.put.assert_called_once_with(
            self.cert_obj_json)

    def test_dequeue_mod_san_request(self):
        self.zk_queue.dequeue_mod_san_request()
        self.zk_queue.dequeue_mod_san_request(False)

        calls = [mock.call(), mock.call()]
        self.zk_queue.mod_san_queue_backend.get.assert_has_calls(calls)
        self.zk_queue.mod_san_queue_backend.consume.assert_called_once_with()
