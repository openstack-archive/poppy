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

import cassandra
import ddt
import mock
from oslo.config import cfg

from poppy.model.helpers import provider_details
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

        # stubbed cassandra driver
        self.sc = services.ServicesController(cassandra_driver)

    @ddt.file_data('data_get_service.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service(self, value, mock_session, mock_execute):

        # mock the response from cassandra
        mock_execute.execute.return_value = value

        actual_response = self.sc.get(self.project_id, self.service_name)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response.name, self.service_name)

    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service_with_exception(self, mock_session, mock_execute):

        # mock the response from cassandra
        mock_execute.execute.return_value = []

        self.assertRaises(ValueError, self.sc.get,
                          self.project_id, self.service_name)

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_create_service(self, value, mock_session, mock_execute):
        service_obj = req_service.load_from_json(value)
        responses = self.sc.create(self.project_id, service_obj)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(responses, None)

        # TODO(amitgandhinz): need to validate the create to cassandra worked.

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_create_service_exist(self, value, mock_session, mock_execute):
        value.update({'name': self.service_name})
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
        mock_execute.execute.return_value = value

        sc = services.ServicesController(None)
        actual_response = sc.list(self.project_id, None, None)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response[0].name, "mocksite")

    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_delete_service(self, mock_session, mock_execute):
        # mock the response from cassandra
        actual_response = self.sc.delete(self.project_id, self.service_name)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @ddt.file_data('../data/data_update_service.json')
    @mock.patch.object(services.ServicesController, 'session')
    @mock.patch.object(cassandra.cluster.Session, 'execute')
    def test_update_service(self, service_json, mock_session, mock_execute):
        # mock the response from cassandra
        service_obj = req_service.load_from_json(service_json)
        actual_response = self.sc.update(self.project_id,
                                         self.service_name,
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
                                                       self.service_name)
        self.assertTrue("MaxCDN" in actual_response)
        self.assertTrue("Mock" in actual_response)
        self.assertTrue("CloudFront" in actual_response)
        self.assertTrue("Fastly" in actual_response)

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
                access_urls=provider_detail_dict["access_urls"])

        # mock the response from cassandra
        mock_execute.execute.return_value = None

        self.sc.update_provider_details(
            self.project_id,
            self.service_name,
            provider_details_dict)

        # this is for update_provider_details unittest code coverage
        arg_provider_details_dict = {}
        for provider_name in provider_details_dict:
            arg_provider_details_dict[provider_name] = json.dumps({
                "id": provider_details_dict[provider_name].provider_service_id,
                "access_urls": (
                    provider_details_dict[provider_name].access_urls),
                "status": provider_details_dict[provider_name].status,
                "name": provider_details_dict[provider_name].name,
                "error_info": None
            })
        args = {
            'project_id': self.project_id,
            'service_name': self.service_name,
            'provider_details': arg_provider_details_dict
        }

        mock_execute.execute.assert_called_once_with(
            services.CQL_UPDATE_PROVIDER_DETAILS, args)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_session(self, mock_service_database):
        session = self.sc.session
        self.assertNotEqual(session, None)
