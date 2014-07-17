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

import ddt
import fastly
import mock
import random
import unittest

from cdn.provider.fastly import services


@ddt.ddt
class TestServices(unittest.TestCase):

    @ddt.file_data('data_service.json')
    @mock.patch('fastly.FastlyConnection')
    @mock.patch('fastly.FastlyService')
    @mock.patch('fastly.FastlyVersion')
    @mock.patch('cdn.provider.fastly.services.ServiceController.client')
    def test_create(self, service_json, MockConnection,
                    MockService, MockVersion, mock_controllerclient):
        service_name = 'scarborough'
        mock_service_id = '%020x' % random.randrange(16**20)
        mockCreateVersionResp = {
            u'service_id': mock_service_id, u'number': 5}

        service = MockService()
        service.id = mock_service_id
        version = MockVersion(MockConnection, mockCreateVersionResp)
        MockConnection.create_service.return_value = service
        MockConnection.create_version.return_value = version

        # instantiate
        controller = services.ServiceController(None)

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

        MockConnection.create_domain.assert_any_call(
            service.id, version.number, service_json['domains'][0]['domain'])

        MockConnection.create_domain.assert_any_call(
            service.id, version.number, service_json['domains'][1]['domain'])

        MockConnection.create_backend.assert_has_any_call(
            service.id, 1,
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['ssl'],
            service_json['origins'][0]['port'])

        self.assertEqual('domain' in resp['fastly'], True)

    @mock.patch('fastly.FastlyConnection')
    @mock.patch('fastly.FastlyService')
    @mock.patch('cdn.provider.fastly.services.ServiceController.client')
    def test_delete(self, mock_connection, mock_service, mock_get_client):
        service_name = 'whatsitnamed'

        # instantiate
        controller = services.ServiceController(None)

        # mock.patch return values
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

    @mock.patch('cdn.provider.fastly.services.ServiceController.client')
    def test_update(self, mock_get_client):
        controller = services.ServiceController(None)
        resp = controller.update(None, None)
        self.assertEqual(resp, None)

    @mock.patch('cdn.provider.fastly.driver.CDNProvider')
    def test_client(self, MockDriver):
        driver = MockDriver()
        controller = services.ServiceController(driver)
        self.assertNotEquals(controller.client(), None)
