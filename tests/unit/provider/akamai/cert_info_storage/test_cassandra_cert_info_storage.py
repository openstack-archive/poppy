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

from poppy.provider.akamai.cert_info_storage import cassandra_storage
from tests.unit import base


@ddt.ddt
class TestCassandraCertInfoStorage(base.TestCase):

    def setUp(self):
        super(TestCassandraCertInfoStorage, self).setUp()

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

        self.default_limit = 80
        self.get_returned_value = [{'info': {
            'san_info':
                '{"secure2.san1.test-cdn.com": '
                '    {"ipVersion": "ipv4", "issuer": "symentec", '
                '     "slot_deployment_klass": "esslType", "jobId": "4312"},'
                '"secure1.san1.test-cdn.com": '
                '{"ipVersion": "ipv4", "issuer": "symentec", '
                '"slot_deployment_klass": "esslType", '
                '"jobId": "1432", "spsId": 1423}}',
            'settings': '{"san_cert_hostname_limit": 80}'
        }}]

    @mock.patch.object(
        cassandra_storage,
        '_DEFAULT_OPTIONS',
        new=[
            cfg.StrOpt('datacenter', default=''),
            cfg.BoolOpt('use_same_storage_driver', default=False)
        ]
    )
    def test_usage_non_shared_cassandra_cluster(self):
        with mock.patch(
            'poppy.storage.cassandra.driver.CassandraStorageDriver'
        ) as mock_driver:
            mock_d = mock.Mock()
            mock_d.cassandra_conf.consistency_level = 'ONE'
            mock_driver.return_value = mock_d
            cass = cassandra_storage.CassandraSanInfoStorage(
                self.conf
            )

        self.assertTrue(cass.storage.change_config_group.called)

    def test__get_akamai_provider_info(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        res = self.cassandra_storage._get_akamai_provider_info()
        mock_execute.assert_called()
        self.assertTrue(res == self.get_returned_value[0])

    def test__get_akamai_san_certs_info(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        res = self.cassandra_storage._get_akamai_san_certs_info()
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info'])
        )

    def test_list_all_san_cert_names(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        res = self.cassandra_storage.list_all_san_cert_names()
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info']).
            keys()
        )

    @ddt.data("secure1.san1.test-cdn.com", "secure2.san1.test-cdn.com")
    def test_save_cert_last_spsid(self, san_cert_name):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        self.cassandra_storage.save_cert_last_ids(
            san_cert_name,
            '1234'
        )
        self.assertTrue(mock_execute.call_count == 3)

    @ddt.data("secure1.san1.test-cdn.com", "secure2.san1.test-cdn.com")
    def test_save_cert_last_spsid_with_job_id(self, san_cert_name):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        self.cassandra_storage.save_cert_last_ids(
            san_cert_name,
            '1234',
            job_id_value=7777
        )
        self.assertTrue(mock_execute.call_count == 3)

    def test_get_cert_last_spsid(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        cert_name = "secure1.san1.test-cdn.com"

        res = self.cassandra_storage.get_cert_last_spsid(
            cert_name
        )
        mock_execute.assert_called()
        self.assertTrue(
            res == json.loads(self.get_returned_value[0]['info']['san_info'])
            [cert_name]['spsId']
        )

    def test_update_san_info(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        self.cassandra_storage.update_san_info({})
        mock_execute.assert_called()

    def test_get_cert_config(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        cert_name = "secure1.san1.test-cdn.com"

        res = self.cassandra_storage.get_cert_config(
            cert_name
        )
        mock_execute.assert_called()
        self.assertTrue(
            res['spsId'] == str(json.loads(
                self.get_returned_value[0]['info']['san_info']
                )[cert_name]['spsId'])
        )

    def test_update_cert_config(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf)
        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value
        cert_name = "secure1.san1.test-cdn.com"
        new_spsId = 3456

        self.cassandra_storage.update_cert_config(
            cert_name, {'spsId': new_spsId}
        )
        mock_execute.assert_called()

    def test_set_san_cert_hostname_limit(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf
        )

        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        self.cassandra_storage.set_san_cert_hostname_limit(99)

        mock_execute.assert_called()

    def test_get_san_cert_hostname_limit(self):
        self.cassandra_storage = cassandra_storage.CassandraSanInfoStorage(
            self.conf
        )

        mock_execute = self.cassandra_storage.session.execute
        mock_execute.return_value = self.get_returned_value

        res = self.cassandra_storage.get_san_cert_hostname_limit()

        mock_execute.assert_called()
        self.assertEqual(res, self.default_limit)
