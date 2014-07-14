import cassandra

from cdn.storage.cassandra.driver import StorageDriver
from cdn.storage.cassandra.services import ServicesController
from ddt import ddt, file_data
from mock import patch
from oslo.config import cfg
from unittest import TestCase


@ddt
class CassandraStorageServiceTests(TestCase):

    def setUp(self):
        # mock arguments to use
        self.project_id = '123456'
        self.service_name = 'mocksite'

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        cassandra_driver = StorageDriver(conf, None)

        # stubbed cassandra driver
        self.sc = ServicesController(cassandra_driver)

    @file_data('data_get_service.json')
    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service(self, value, mock_session, mock_execute):

        # mock the response from cassandra
        mock_execute.execute.return_value = value

        actual_response = self.sc.get(self.project_id, self.service_name)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response[0][0], self.project_id)
        self.assertEqual(actual_response[0][1], self.service_name)

    @file_data('data_create_service.json')
    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_create_service(self, value, mock_session, mock_execute):
        responses = self.sc.create(self.project_id, self.service_name, value)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(responses, None)

        # TODO(amitgandhinz): need to validate the create to cassandra worked.

    @file_data('data_list_services.json')
    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_list_services(self, value, mock_session, mock_execute):
        # mock the response from cassandra
        mock_execute.execute.return_value = value

        sc = ServicesController(None)
        actual_response = sc.list(self.project_id)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response[0][0], self.project_id)
        self.assertEqual(actual_response[0][1], "mocksite")

    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_delete_service(self, mock_session, mock_execute):
        # mock the response from cassandra
        actual_response = self.sc.delete(self.project_id, self.service_name)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @file_data('data_update_service.json')
    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_update_service(self, value, mock_session, mock_execute):
        # mock the response from cassandra
        actual_response = self.sc.update(self.project_id,
                                         self.service_name,
                                         value)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @patch.object(cassandra.cluster.Cluster, 'connect')
    def test_session(self, mock_service_database):
        session = self.sc.session
        self.assertIsNotNone(session)
