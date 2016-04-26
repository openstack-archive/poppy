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

import uuid

import cassandra
import ddt
import mock
from oslo_config import cfg

from poppy.model import ssl_certificate
from poppy.storage.cassandra import certificates
from poppy.storage.cassandra import driver
from tests.unit import base


@ddt.ddt
class CassandraStorageServiceTests(base.TestCase):

    def setUp(self):
        super(CassandraStorageServiceTests, self).setUp()

        # mock arguments to use
        self.project_id = '123456'
        self.service_id = uuid.uuid4()
        self.service_name = 'mocksite'

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        conf.register_opt(
            cfg.StrOpt(
                'datacenter',
                default='',
                help='datacenter where the C* cluster hosted'))
        conf.register_opts(driver.CASSANDRA_OPTIONS,
                           group=driver.CASSANDRA_GROUP)
        cassandra_driver = driver.CassandraStorageDriver(conf)

        migrations_patcher = mock.patch(
            'cdeploy.migrator.Migrator'
        )
        migrations_patcher.start()
        self.addCleanup(migrations_patcher.stop)

        # stubbed cassandra driver
        self.cc = certificates.CertificatesController(cassandra_driver)

    @ddt.file_data('data_get_certs_by_domain.json')
    @mock.patch.object(certificates.CertificatesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_certs_by_domain(self, cert_details_json,
                                 mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = cert_details_json[0]
        actual_response = self.cc.get_certs_by_domain(
            domain_name="www.mydomain.com"
        )
        self.assertEqual(len(actual_response), 2)
        self.assertTrue(all([isinstance(ssl_cert,
                                        ssl_certificate.SSLCertificate)
                             for ssl_cert in actual_response]))
        mock_execute.execute.return_value = cert_details_json[1]
        actual_response = self.cc.get_certs_by_domain(
            domain_name="www.example.com",
            flavor_id="flavor1")
        self.assertEqual(len(actual_response), 2)
        self.assertTrue(all([isinstance(ssl_cert,
                                        ssl_certificate.SSLCertificate)
                             for ssl_cert in actual_response]))
        mock_execute.execute.return_value = cert_details_json[2]
        actual_response = self.cc.get_certs_by_domain(
            domain_name="www.mydomain.com",
            flavor_id="flavor1",
            cert_type="san")
        self.assertTrue(isinstance(actual_response,
                                   ssl_certificate.SSLCertificate))

    @mock.patch.object(certificates.CertificatesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_certs_by_status(self, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = \
            [{"domain_name": "www.example.com"}]
        actual_response = self.cc.get_certs_by_status(
            status="deployed")
        self.assertEqual(actual_response,
                         [{"domain_name": "www.example.com"}])

        mock_execute.execute.return_value = \
            [{"domain_name": "www.example1.com"}]
        actual_response = self.cc.get_certs_by_status(
            status="failed")
        self.assertEqual(actual_response,
                         [{"domain_name": "www.example1.com"}])
