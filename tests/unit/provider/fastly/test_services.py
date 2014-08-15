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
        provider_service_id = 3488

        # instantiate
        controller = services.ServiceController(driver)

        # mock.patch return values
        service = mock_service()
        service.id = 3488
        controller.client.get_service_by_name.return_value = service

        # test exception
        exception = fastly.FastlyError(Exception('ding'))
        controller.client.delete_service.side_effect = exception
        resp = controller.delete(provider_service_id)

        self.assertIn('error', resp[driver.provider_name])

        # clear run
        controller.client.reset_mock()
        controller.client.delete_service.side_effect = None

        resp = controller.delete(provider_service_id)
        # controller.client.get_service_by_name.assert_called_once_with(
        #    service_name)
        controller.client.delete_service.assert_called_once_with(
            provider_service_id)
        self.assertIn('id', resp[driver.provider_name])

    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    @ddt.file_data('data_service.json')
    def test_update(self, mock_get_client, mock_driver, service_json):
        provider_service_id = 3488
        driver = mock_driver()
        controller = services.ServiceController(driver)
        resp = controller.update(provider_service_id, service_json)
        self.assertIn('id', resp[driver.provider_name])

    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def test_client(self, mock_driver):
        driver = mock_driver()
        controller = services.ServiceController(driver)
        self.assertNotEqual(controller.client(), None)
