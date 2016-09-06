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

from poppy.provider.akamai.domain_san_mapping_queue import zk_san_mapping_queue
from tests.unit import base


class TestSanMappingQueue(base.TestCase):

    def setUp(self):
        super(TestSanMappingQueue, self).setUp()
        self.san_mapping_dict = {
            "domain_name": "test-san1.cnamecdn.com",
            "flavor_id": "flavor_id",
            "project_id": "project_id",
            "cert_type": "san",
            "cert_details": {
                "Akamai": {
                    "extra_info": {
                        "san cert": "san1.example.com",
                        "akamai_spsId": 1
                    }
                }
            }
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
        self.zk_queue = zk_san_mapping_queue.ZookeeperSanMappingQueue(
            self.conf)

    def test_enqueue_san_mapping(self):
        self.zk_queue.enqueue_san_mapping(
            json.dumps(self.san_mapping_dict).encode('utf-8'))
        self.assertTrue(len(self.zk_queue.san_mapping_queue_backend) == 1)
        self.assertTrue(
            json.loads(self.zk_queue.san_mapping_queue_backend.get().
                       decode('utf-8')) == self.san_mapping_dict)

    def test_dequeue_san_mapping(self):
        self.zk_queue.enqueue_san_mapping(
            json.dumps(self.san_mapping_dict).encode('utf-8'))
        res = self.zk_queue.dequeue_san_mapping(False).decode('utf-8')
        self.assertTrue(len(self.zk_queue.san_mapping_queue_backend) == 1)
        self.assertTrue(json.loads(res) == self.san_mapping_dict)

        res = self.zk_queue.dequeue_san_mapping().decode('utf-8')
        self.assertTrue(len(self.zk_queue.san_mapping_queue_backend) == 0)
        self.assertTrue(json.loads(res) == self.san_mapping_dict)

    def test_traverse_queue(self):
        self.zk_queue.enqueue_san_mapping(
            json.dumps(self.san_mapping_dict).encode('utf-8'))
        res = self.zk_queue.traverse_queue()
        self.assertTrue(len(res) == 1)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == [self.san_mapping_dict])

    def test_traverse_queue_consume(self):
        self.zk_queue.enqueue_san_mapping(
            json.dumps(self.san_mapping_dict).encode('utf-8'))
        res = self.zk_queue.traverse_queue(consume=True)
        self.assertTrue(len(res) == 1)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == [self.san_mapping_dict])

    def test_traverse_queue_multiple_records(self):
        # Get a list of records to enqueue
        san_mapping_list = []
        for i in range(10):
            mapping_object = {
                "domain_name": "domain.domain{0}.com".format(i),
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san1.example.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            }
            san_mapping_list.append(mapping_object)

        for cert_obj in san_mapping_list:
            self.zk_queue.enqueue_san_mapping(
                json.dumps(cert_obj).encode('utf-8'))
        res = self.zk_queue.traverse_queue()
        self.assertTrue(len(res) == 10)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == san_mapping_list)

    def test_put_queue_data(self):
        res = self.zk_queue.put_queue_data([])
        self.assertTrue(len(res) == 0)

        san_mapping_list = []
        for i in range(10):
            mapping_object = {
                "domain_name": "domain.domain{0}.com".format(i),
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san1.example.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            }
            san_mapping_list.append(mapping_object)

        self.zk_queue.put_queue_data(
            [json.dumps(o).encode('utf-8') for o in san_mapping_list])
        self.assertTrue(len(self.zk_queue.san_mapping_queue_backend) == 10)
        res = self.zk_queue.traverse_queue()
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == san_mapping_list)

        # test put data to non-empty queue
        # should replace all items added above
        self.zk_queue.put_queue_data(
            [json.dumps(o).encode('utf-8') for o in san_mapping_list])
        self.assertTrue(len(self.zk_queue.san_mapping_queue_backend) == 10)
