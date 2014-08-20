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
import random
import uuid

import ddt
import fastly
import mock

from poppy.provider.fastly import services
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @ddt.file_data('data_service.json')
    @mock.patch('fastly.FastlyConnection')
    @mock.patch('fastly.FastlyService')
    @mock.patch('fastly.FastlyVersion')
    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def test_create(self, service_json, mock_connection,
                    mock_service, mock_version, mock_controllerclient,
                    mock_driver):
        driver = mock_driver()
        driver.provider_name = 'Fastly'

        # instantiate
        controller = services.ServiceController(driver)

        service_name = 'scarborough'
        mock_service_id = '%020x' % random.randrange(16 ** 20)
        mock_create_version_resp = {
            u'service_id': mock_service_id, u'number': 5}

        service = mock_service()
        service.id = mock_service_id
        version = mock_version(controller.client, mock_create_version_resp)
        controller.client.create_service.return_value = service
        controller.client.create_version.return_value = version

        # ASSERTIONS
        # create_service
        controller.client.create_service.side_effect = fastly.FastlyError(
            Exception('Creating service failed.'))
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_service.side_effect = None

        # create_version
        controller.client.create_version.side_effect = fastly.FastlyError(
            Exception('Creating version failed.'))
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_version.side_effect = None

        # create domains
        controller.client.create_domain.side_effect = fastly.FastlyError(
            Exception('Creating domains failed.'))
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_domain.side_effect = None

        # create backends
        controller.client.create_backend.side_effect = fastly.FastlyError(
            Exception('Creating backend failed.'))
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_backend.side_effect = None

        controller.client.check_domains.side_effect = fastly.FastlyError(
            Exception('Check_domains failed.'))
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.check_domains.side_effect = None

        # test a general exception
        controller.client.create_service.side_effect = Exception(
            'Wild exception occurred.')
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        # finally, a clear run
        controller.client.reset_mock()
        controller.client.create_service.side_effect = None

        controller.client.check_domains.return_value = [
            [{
             "name": "www.example.com",
             "comment": "",
             "service_id": "<fake_id>",
             "version": "1",
             "locked": True
             },
             "global.prod.fastly.net.",
             True
             ]
        ]

        resp = controller.create(service_name, service_json)

        controller.client.create_service.assert_called_once_with(
            controller.current_customer.id, service_name)

        controller.client.create_version.assert_called_once_with(service.id)

        controller.client.create_domain.assert_any_call(
            service.id, version.number, service_json['domains'][0]['domain'])

        controller.client.create_domain.assert_any_call(
            service.id, version.number, service_json['domains'][1]['domain'])

        controller.client.check_domains.assert_called_once_with(
            service.id, version.number)

        controller.client.create_backend.assert_has_any_call(
            service.id, 1,
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['origin'],
            service_json['origins'][0]['ssl'],
            service_json['origins'][0]['port'])

        self.assertIn('links', resp[driver.provider_name])

    @mock.patch('fastly.FastlyConnection')
    @mock.patch('fastly.FastlyService')
    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def test_delete(self, mock_connection, mock_service, mock_client,
                    mock_driver):
        driver = mock_driver()
        driver.provider_name = 'Fastly'
        service_name = 'whatsitnamed'

        # instantiate
        controller = services.ServiceController(driver)

        # mock.patch return values
        service = mock_service()
        service.id = '1234'
        controller.client.get_service_by_name.return_value = service

        # test exception
        exception = fastly.FastlyError(Exception('ding'))
        controller.client.delete_service.side_effect = exception
        resp = controller.delete('wrongname')

        self.assertIn('error', resp[driver.provider_name])

        # clear run
        controller.client.reset_mock()
        controller.client.delete_service.side_effect = None

        resp = controller.delete(service_name)
        controller.client.get_service_by_name.assert_called_once_with(
            service_name)
        controller.client.delete_service.assert_called_once_with(service.id)
        self.assertIn('id', resp[driver.provider_name])

    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    @ddt.file_data('data_service.json')
    def test_update(self, mock_get_client, mock_driver, service_json):
        service_name = 'whatsitnamed'

        driver = mock_driver()
        controller = services.ServiceController(driver)
        resp = controller.update(service_name, service_json)
        self.assertIn('id', resp[driver.provider_name])

    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def test_client(self, mock_driver):
        driver = mock_driver()
        controller = services.ServiceController(driver)
        self.assertNotEqual(controller.client(), None)


class TestProviderValidation(base.TestCase):
    """Tests for provider side validation methods.

    This class tests the validation methods to verify the data accuracy
    at the provider side.
    """

    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def setUp(self, mock_client, mock_driver):
        super(TestProviderValidation, self).setUp()

        self.driver = mock_driver()
        self.controller = services.ServiceController(self.driver)
        self.client = mock_client
        self.service_name = uuid.uuid1()
        service_json = {"domains": [{"domain": "parsely.sage.com"}],
                        "origins": [{"origin": "mockdomain.com",
                                     "ssl": False, "port": 80}]}
        self.controller.create(self.service_name, service_json)

    @mock.patch('fastly.FastlyService')
    def test_get_service_details(self, mock_service):

        service = mock_service()
        service.id = '1234'
        service.version = [{'number': 1}]

        self.controller.client.get_service_by_name.return_value = service

        self.controller.client.list_domains.return_value = (
            [{u'comment': u'A new domain.',
              u'service_id': u'75hthkv6jrGW4aVjSReT0w', u'version': 1,
              u'name': u'www.testr.com'}])

        self.controller.client.list_cache_settings.return_value = (
            [{u'stale_ttl': u'0', u'name': u'test-cache', u'ttl': u'3600',
              u'version': u'1', u'cache_condition': '', u'action': '',
              u'service_id': u'75hthkv6jrGW4aVjSReT0w'}])

        self.controller.client.list_backends.return_value = (
            [{u'comment': '', u'shield': None, u'weight': 100,
              u'between_bytes_timeout': 10000, u'ssl_client_key': None,
              u'first_byte_timeout': 15000, u'auto_loadbalance': False,
              u'use_ssl': False, u'port': 80, u'ssl_hostname': None,
              u'hostname': u'www.testr.com', u'error_threshold': 0,
              u'max_conn': 20, u'version': 1, u'ipv4': None, u'ipv6': None,
              u'connect_timeout': 1000, u'ssl_ca_cert': None,
              u'request_condition': '', u'healthcheck': None,
              u'address': u'www.testr.com', u'ssl_client_cert': None,
              u'name': u'bbb', u'client_cert': None,
              u'service_id': u'75hthkv6jrGW4aVjSReT0w'}])

        resp = self.controller.get(self.service_name)

        self.assertEqual(resp[self.driver.provider_name]['domains'],
                         ['www.testr.com'])

        self.assertEqual(resp[self.driver.provider_name]['caching'],
                         [{'name': 'test-cache', 'ttl': 3600, 'rules': ''}])

        self.assertEqual(resp[self.driver.provider_name]['origins'],
                         [{'origin': u'www.testr.com', 'port': 80,
                           'ssl': False}])

    def test_get_service_details_error(self):
        error = fastly.FastlyError('DIMMM')
        self.controller.client.get_service_by_name.side_effect = error
        resp = self.controller.get('rror-service')

        self.assertIn('error', resp[self.driver.provider_name])

    def test_get_service_details_exception(self):
        exception = Exception('DOOM')
        self.controller.client.get_service_by_name.side_effect = exception
        resp = self.controller.get('magic-service')

        self.assertIn('error', resp[self.driver.provider_name])
