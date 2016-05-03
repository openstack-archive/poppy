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

from poppy.provider.akamai.cert_info_storage import zookeeper_storage
from tests.unit import base

AKAMAI_OPTIONS = [
    # storage backend configs for long running tasks
    cfg.StrOpt(
        'storage_backend_type',
        help='SAN Cert info storage backend'),
    cfg.ListOpt('storage_backend_host', default=['localhost'],
                help='default san info storage backend server hosts'),
    cfg.IntOpt('storage_backend_port', default=2181, help='default'
               ' default san info storage backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'cert_info_storage_path',
        default='/cert_info',
        help='zookeeper backend'
        ' path for san cert info'
    ),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class TestZookeeperCertInfoStorage(base.TestCase):

    def setUp(self):
        super(TestZookeeperCertInfoStorage, self).setUp()
        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient'
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

        self.conf = cfg.ConfigOpts()
        self.zk_storage = zookeeper_storage.ZookeeperSanInfoStorage(self.conf)

        def zk_get_value_func(zk_path):
            stat = "good"
            if 'jobId' in zk_path:
                return stat, 1789
            if 'spsId' in zk_path:
                return stat, 4809
            if 'issuer' in zk_path:
                return stat, 'symantec'
            if 'ipVersion' in zk_path:
                return stat, 'ipv4'
            if 'slot_deployment_klass' in zk_path:
                return stat, 'esslType'
            return None, None
        self.zk_storage.zookeeper_client.get.side_effect = zk_get_value_func

    def test__zk_path(self):
        path1 = self.zk_storage._zk_path('secure.san1.poppycdn.com', 'jobId')
        self.assertTrue(path1 == '/cert_info/secure.san1.poppycdn.com/jobId')

        path2 = self.zk_storage._zk_path('secure.san1.poppycdn.com', None)
        self.assertTrue(path2 == '/cert_info/secure.san1.poppycdn.com')

    def test__save_cert_property_value(self):
        self.zk_storage._save_cert_property_value('secure.san1.poppycdn.com',
                                                  'spsId', str(1789))
        self.zk_storage.zookeeper_client.ensure_path.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId')
        self.zk_storage.zookeeper_client.set.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId', str(1789))

    def test_save_cert_last_spsid(self):
        self.zk_storage.save_cert_last_ids('secure.san1.poppycdn.com', 1789)
        self.zk_storage.zookeeper_client.ensure_path.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId')
        self.zk_storage.zookeeper_client.set.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId', str(1789))

    def test_save_cert_last_spsid_with_job_id(self):
        self.zk_storage.save_cert_last_ids(
            'secure.san1.poppycdn.com',
            1789,
            job_id_value=7777
        )
        self.zk_storage.zookeeper_client.ensure_path.assert_has_calls(
            [
                mock.call('/cert_info/secure.san1.poppycdn.com/spsId'),
                mock.call('/cert_info/secure.san1.poppycdn.com/jobId')
            ]
        )
        self.zk_storage.zookeeper_client.set.assert_has_calls(
            [mock.call('/cert_info/secure.san1.poppycdn.com/spsId', str(1789)),
             mock.call('/cert_info/secure.san1.poppycdn.com/jobId', str(7777))]
        )

    def test_get_cert_last_spsid(self):
        self.zk_storage.get_cert_last_spsid('secure.san1.poppycdn.com')
        self.zk_storage.zookeeper_client.ensure_path.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId')
        self.zk_storage.zookeeper_client.get.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com/spsId')

    def list_all_san_cert_names(self):
        self.zk_storage.list_all_san_cert_names()
        self.zk_storage.zookeeper_client.get_children.assert_create_once_with(
            '/cert_info/secure.san1.poppycdn.com'
        )

    def test_get_cert_info(self):
        res = self.zk_storage.get_cert_info('secure.san1.poppycdn.com')
        self.zk_storage.zookeeper_client.ensure_path.assert_called_once_with(
            '/cert_info/secure.san1.poppycdn.com'
        )
        calls = [mock.call('/cert_info/secure.san1.poppycdn.com/jobId'),
                 mock.call('/cert_info/secure.san1.poppycdn.com/issuer'),
                 mock.call('/cert_info/secure.san1.poppycdn.com/ipVersion'),
                 mock.call(
            '/cert_info/secure.san1.poppycdn.com/slot_deployment_klass')]
        self.zk_storage.zookeeper_client.get.assert_has_calls(calls)
        self.assertTrue(isinstance(res, dict))
