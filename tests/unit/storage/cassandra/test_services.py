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

import json
import uuid
try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

import cassandra
import ddt
import mock
from oslo_config import cfg

from poppy.model.helpers import provider_details
from poppy.model import ssl_certificate
from poppy.storage.cassandra import driver
from poppy.storage.cassandra import services
from poppy.transport.pecan.models.request import service as req_service
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
        self.sc = services.ServicesController(cassandra_driver)

    @ddt.file_data('data_get_service.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service(self, value, mock_session, mock_execute):

        # mock the response from cassandra
        value[0]['service_id'] = self.service_id
        mock_execute.execute.return_value = value

        actual_response = self.sc.get(self.project_id, self.service_id)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(str(actual_response.service_id), str(self.service_id))

    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service_with_exception(self, mock_session, mock_execute):

        # mock the response from cassandra
        mock_execute.execute.return_value = []

        self.assertRaises(ValueError, self.sc.get,
                          self.project_id, self.service_id)

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=False)
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_create_service(self, value,
                            mock_check, mock_session, mock_execute):
        service_obj = req_service.load_from_json(value)
        responses = self.sc.create(self.project_id, service_obj)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(responses, None)

        # TODO(amitgandhinz): need to validate the create to cassandra worked.

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=True)
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_create_service_exist(self, value,
                                  mock_check, mock_session, mock_execute):
        service_obj = req_service.load_from_json(value)
        self.sc.get = mock.Mock(return_value=service_obj)

        self.assertRaises(ValueError,
                          self.sc.create,
                          self.project_id, service_obj)

    @ddt.file_data('data_list_services.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_list_services(self, value, mock_session, mock_execute):
        # mock the response from cassandra
        value[0]['project_id'] = self.project_id
        mock_execute.prepare.return_value = mock.Mock()
        mock_execute.execute.return_value = value

        actual_response = self.sc.list(self.project_id, None, None)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response[0].name, "mocksite")
        self.assertEqual(actual_response[0].project_id, self.project_id)

    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_delete_service(self, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = iter([{}])
        actual_response = self.sc.delete(self.project_id, self.service_id)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @ddt.file_data('../data/data_update_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=False)
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_update_service(self, service_json,
                            mock_execute, mock_session, mock_check):
        mock_check.return_value = False
        mock_session.execute.return_value = iter([{}])
        service_obj = req_service.load_from_json(service_json)
        actual_response = self.sc.update(self.project_id,
                                         self.service_id,
                                         service_obj)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @ddt.file_data('data_provider_details.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_provider_details(self, provider_details_json,
                                  mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = [{'provider_details':
                                              provider_details_json}]
        actual_response = self.sc.get_provider_details(self.project_id,
                                                       self.service_id)
        self.assertTrue("MaxCDN" in actual_response)
        self.assertTrue("Mock" in actual_response)
        self.assertTrue("CloudFront" in actual_response)
        self.assertTrue("Fastly" in actual_response)

    @ddt.file_data('data_get_certs_by_domain.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_certs_by_domain(self, cert_details_json,
                                 mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = cert_details_json[0]
        actual_response = self.sc.get_certs_by_domain(
            domain_name="www.mydomain.com")
        self.assertEqual(len(actual_response), 2)
        self.assertTrue(all([isinstance(ssl_cert,
                                        ssl_certificate.SSLCertificate)
                             for ssl_cert in actual_response]))
        mock_execute.execute.return_value = cert_details_json[1]
        actual_response = self.sc.get_certs_by_domain(
            domain_name="www.example.com",
            flavor_id="flavor1")
        self.assertEqual(len(actual_response), 2)
        self.assertTrue(all([isinstance(ssl_cert,
                                        ssl_certificate.SSLCertificate)
                             for ssl_cert in actual_response]))
        mock_execute.execute.return_value = cert_details_json[2]
        actual_response = self.sc.get_certs_by_domain(
            domain_name="www.mydomain.com",
            flavor_id="flavor1",
            cert_type="san")
        self.assertTrue(isinstance(actual_response,
                                   ssl_certificate.SSLCertificate))

    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_certs_by_status(self, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = \
            [{"domain_name": "www.example.com"}]
        actual_response = self.sc.get_certs_by_status(
            status="deployed")
        self.assertEqual(actual_response,
                         [{"domain_name": "www.example.com"}])

        mock_execute.execute.return_value = \
            [{"domain_name": "www.example1.com"}]
        actual_response = self.sc.get_certs_by_status(
            status="failed")
        self.assertEqual(actual_response,
                         [{"domain_name": "www.example1.com"}])

    @ddt.file_data('data_provider_details.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_update_provider_details(self, provider_details_json,
                                     mock_session, mock_execute):
        provider_details_dict = {}
        for k, v in provider_details_json.items():
            provider_detail_dict = json.loads(v)

            provider_details_dict[k] = provider_details.ProviderDetail(
                provider_service_id=(
                    provider_detail_dict["id"]),
                access_urls=provider_detail_dict["access_urls"],
                domains_certificate_status=provider_detail_dict.get(
                    "domains_certificate_status", {}))

        # mock the response from cassandra
        mock_execute.execute.return_value = None

        # this is for update_provider_details unittest code coverage
        arg_provider_details_dict = {}
        status = None
        for provider_name in provider_details_dict:
            the_provider_detail_dict = collections.OrderedDict()
            the_provider_detail_dict["id"] = (
                provider_details_dict[provider_name].provider_service_id)
            the_provider_detail_dict["access_urls"] = (
                provider_details_dict[provider_name].access_urls)
            the_provider_detail_dict["status"] = (
                provider_details_dict[provider_name].status)
            status = the_provider_detail_dict["status"]
            the_provider_detail_dict["name"] = (
                provider_details_dict[provider_name].name)
            the_provider_detail_dict["domains_certificate_status"] = (
                provider_details_dict[provider_name].
                domains_certificate_status.to_dict())
            the_provider_detail_dict["error_info"] = (
                provider_details_dict[provider_name].error_info)
            the_provider_detail_dict["error_message"] = (
                provider_details_dict[provider_name].error_message)
            arg_provider_details_dict[provider_name] = json.dumps(
                the_provider_detail_dict)

        provider_details_args = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'provider_details': arg_provider_details_dict
        }
        status_args = {
            'status': status,
            'project_id': self.project_id,
            'service_id': self.service_id
        }
        # This is to verify mock has been called with the correct arguments

        def assert_mock_execute_args(*args):

            if args[0].query_string == services.CQL_UPDATE_PROVIDER_DETAILS:
                self.assertEqual(args[1], provider_details_args)
            elif args[0].query_string == services.CQL_SET_SERVICE_STATUS:
                self.assertEqual(args[1], status_args)

        mock_execute.execute.side_effect = assert_mock_execute_args

        self.sc.update_provider_details(
            self.project_id,
            self.service_id,
            provider_details_dict)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_session(self, mock_service_database):
        session = self.sc.session
        self.assertNotEqual(session, None)
