from mock import patch
import unittest
from ddt import ddt, file_data
import fastly

from cdn.provider.fastly.services import ServiceController
from cdn.provider.fastly.driver import CDNProvider


@ddt
class TestServices(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @file_data('data_service.json')
    @patch('fastly.FastlyConnection')
    @patch('fastly.FastlyService')
    @patch('fastly.FastlyVersion')
    @patch('cdn.provider.fastly.services.ServiceController.client')
    def test_create(self, service_json, MockConnection,
                    MockService, MockVersion, mock_controllerclient):
        service_name = 'scarborough'
        mockCreateVersionResp = {
            u'service_id': u'296GKB0evsdjqwh2RalZl8', u'number': 5}

        service = MockService()
        service.id = '1234'
        version = MockVersion(MockConnection, mockCreateVersionResp)
        MockConnection.create_service.return_value = service
        MockConnection.create_version.return_value = version

        # instantiate
        controller = ServiceController(None)

        # ASSERTIONS
        # create_service
        MockConnection.create_service.side_effect = fastly.FastlyError(
            Exception('Creating service failed.'))
        resp = controller.create(service_name, service_json)
        self.assertEqual('error' in resp['fastly'], True)

        MockConnection.reset_mock()
        MockConnection.create_service.side_effect = None

        # create_version
        MockConnection.create_version.side_effect = fastly.FastlyError(
            Exception('Creating version failed.'))
        resp = controller.create(service_name, service_json)
        self.assertEqual('error' in resp['fastly'], True)

        MockConnection.reset_mock()
        MockConnection.create_version.side_effect = None

        # create domains
        MockConnection.create_domain.side_effect = fastly.FastlyError(
            Exception('Creating domains failed.'))
        resp = controller.create(service_name, service_json)
        self.assertEqual('error' in resp['fastly'], True)

        MockConnection.reset_mock()
        MockConnection.create_domain.side_effect = None

        # create backends
        MockConnection.create_backend.side_effect = fastly.FastlyError(
            Exception('Creating backend failed.'))
        resp = controller.create(service_name, service_json)
        self.assertEqual('error' in resp['fastly'], True)

        MockConnection.reset_mock()
        MockConnection.create_backend.side_effect = None

        # test a general exception
        MockConnection.create_service.side_effect = Exception(
            'Wild exception occurred.')
        resp = controller.create(service_name, service_json)
        self.assertEqual('error' in resp['fastly'], True)

        # finally, a clear run
        MockConnection.reset_mock()
        MockConnection.create_service.side_effect = None

        resp = controller.create(service_name, service_json)

        MockConnection.create_service.assert_called_once_with(
                controller.current_customer.id, service_name)

        MockConnection.create_version.assert_called_once_with(service.id)

        MockConnection.create_domain.assert_any_call(service.id,
                version.number, service_json['domains'][0]['domain'])

        MockConnection.create_domain.assert_any_call(service.id,
                version.number, service_json['domains'][1]['domain'])

        MockConnection.create_backend.assert_has_any_call(
            service.id, 1,
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['ssl'],
            service_json['origins'][0]['port'])

        self.assertEqual('domain' in resp['fastly'], True)

    @patch('fastly.FastlyConnection')
    @patch('fastly.FastlyService')
    @patch('cdn.provider.fastly.services.ServiceController.client')
    def test_delete(self, mock_connection, mock_service, mock_get_client):
        service_name = 'whatsitnamed'

        # instantiate
        controller = ServiceController(None)

        # patch return values
        service = mock_service()
        service.id = '1234'
        controller.client.get_service_by_name.return_value = service

        # test exception
        exception = fastly.FastlyError(Exception('ding'))
        mock_connection.delete_service.side_effect = exception
        resp = controller.delete('wrongname')
        self.assertEqual('error' in resp['fastly'], True)

        # clear run
        mock_connection.reset_mock()
        mock_connection.delete_service.side_effect = None

        resp = controller.delete(service_name)
        mock_connection.get_service_by_name.assert_called_once_with(
            service_name)
        mock_connection.delete_service.assert_called_once_with(service.id)
        self.assertEqual('domain' in resp['fastly'], True)

    @patch('cdn.provider.fastly.services.ServiceController.client')
    def test_update(self, mock_get_client):
        controller = ServiceController(None)
        resp = controller.update(None, None)
        self.assertEqual(resp, None)

    @patch('cdn.provider.fastly.driver.CDNProvider')
    def test_client(self, MockDriver):
        driver = MockDriver()
        controller = ServiceController(driver)
        self.assertNotEquals(controller.client(), None)
