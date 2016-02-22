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

import json

import ddt
import mock
from oslo_config import cfg

from poppy.provider.akamai.san_info_storage import cassandra_storage
from tests.unit import base


@ddt.ddt
class TestCassandraSANInfoStorage(base.TestCase):

    def setUp(self):
        super(TestCassandraSANInfoStorage, self).setUp()

        # create mocked config and driver
        migrations_patcher = mock.patch(
            'cdeploy.migrator.Migrator'
        )
        migrations_patcher.start()
        self.addCleanup(migrations_patcher.stop)

        cluster_patcher = mock.patch(
            'cassandra.cluster.Cluster'
        )
        cluster_patcher.start()
        self.addCleanup(cluster_patcher.stop)

        self.conf = cfg.ConfigOpts()
        self.cassa_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)

        self.get_returned_value = [{'info': {
            'san_info':
                '{"secure2.san1.test_cdn.com": '
                '    {"ipVersion": "ipv4", "issuer": "symentec", '
                '     "slot_deployment_klass": "esslType", "jobId": "4312"},'
                '"secure1.san1.test_cdn.com": '
                '{"ipVersion": "ipv4", "issuer": "symentec", '
                '"slot_deployment_klass": "esslType", '
                '"jobId": "1432", "spsId": 1423}}'}}]

    def test__get_akamai_provider_info(self):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        res = self.cassa_storage._get_akamai_provider_info()
        mock_execute.assert_called()
        self.assertTrue(res == self.get_returned_value[0])

    def test__get_akamai_san_certs_info(self):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        res = self.cassa_storage._get_akamai_san_certs_info()
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info'])
        )

    def test_list_all_san_cert_names(self):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        res = self.cassa_storage.list_all_san_cert_names()
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info']).
            keys()
        )

    @ddt.data("secure1.san1.test_cdn.com", "secure2.san1.test_cdn.com")
    def test_save_cert_last_spsid(self, san_cert_name):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        self.cassa_storage.save_cert_last_spsid(
            san_cert_name,
            '1234'
        )
        self.assertTrue(mock_execute.call_count == 3)

    def test_get_cert_last_spsid(self):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        cert_name = "secure1.san1.test_cdn.com"

        res = self.cassa_storage.get_cert_last_spsid(
            cert_name
        )
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info'])
            [cert_name]['spsId']
        )

    def test_update_san_info(self):
        mock_execute = self.cassa_storage.session.execute
        self.cassa_storage.update_san_info({})
        mock_execute.assert_called()

    def test_get_cert_config(self):
        mock_execute = self.cassa_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        cert_name = "secure1.san1.test_cdn.com"

        res = self.cassa_storage.get_cert_config(
            cert_name
        )
        mock_execute.assert_called()
        self.assertTrue(
            res['spsId'] == json.loads(
                self.get_returned_value[0]['info']['san_info']
                )[cert_name]['spsId']
        )
