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
import mock
from oslo.config import cfg

from poppy.provider.maxcdn import driver
from poppy.provider.maxcdn import services
from tests.unit import base


MAXCDN_OPTIONS = [
    cfg.StrOpt('alias',
               default='no_good_alias',
               help='MAXCDN API account alias'),
    cfg.StrOpt('consumer_key',
               default='a_consumer_key',
               help='MAXCDN API consumer key'),
    cfg.StrOpt('consumer_secret',
               default='a_consumer_secret',
               help='MAXCDN API consumer secret'),
]


class fake_maxcdn_api_client:

    def get(self, url='/account.json'):
        return {u'code': 200,
                u'data':
                {u'account':
                 {u'status': u'2',
                  u'name': u'<My_fake_company_alias>',
                  u'id': u'32811'
                  }}}

    def post(self, url=None, data=None):
        return {u'code': 201,
                u'data': {
                    u"pullzone": {
                        u"cdn_url": u"newpullzone1.alias.netdna-cdn.com",
                        u'name': u'newpullzone1',
                        u'id': u'97312'
                    }}}

    def put(self, url=None, params=None):
        return {u'code': 200,
                u'data': {
                    u"pullzone": {
                        u"cdn_url": u"newpullzone1.alias.netdna-cdn.com",
                        u'name': u'newpullzone1',
                        u'id': u'97312'
                    }}}

    def delete(self, url=None):
        return {u'code': 200,
                }

fake_maxcdn_client_get_return_value = {u'code': 200,
                                       u'data':
                                       {u'account':
                                        {u'status': u'2',
                                         u'name': u'<My_fake_company_alias>',
                                         u'id': u'32811'
                                         }}}

fake_maxcdn_client_400_return_value = {
    u'code': 400,
    u'message': "operation PUT/GET/POST failed due to technical difficulties.."
}


@ddt.ddt
class TestServices(base.TestCase):

    def setUp(self):
        super(TestServices, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch.object(driver, 'MAXCDN_OPTIONS', new=MAXCDN_OPTIONS)
    def test_init(self):
        provider = driver.CDNProvider(self.conf)
        # instantiate will get
        self.assertRaises(RuntimeError, services.ServiceController, provider)

    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_get(self):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        service_name = "test_service_name"
        self.assertTrue(controller.get(service_name) is not None)

    @ddt.file_data('data_service.json')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_create(self, service_json):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_name = "test_service_name"
        resp = controller.create(service_name, service_json)
        self.assertIn('id', resp[new_driver.provider_name])
        self.assertIn('links', resp[new_driver.provider_name])

    @ddt.file_data('data_service.json')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_create_with_exception(self, service_json, mock_controllerclient,
                                   mock_driver):
        # test create with exceptions
        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'get.return_value':
                                        fake_maxcdn_client_get_return_value
                                        })

        service_name = "test_service_name"

        controller_with_create_exception = services.ServiceController(driver)
        controller_with_create_exception.client.configure_mock(**{
            "post.side_effect":
            RuntimeError('Creating service mysteriously failed.')})
        resp = controller_with_create_exception.create(
            service_name,
            service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller_with_create_exception.client.reset_mock()
        controller_with_create_exception.client.configure_mock(**{
            'post.side_effect': None,
            "post.return_value": fake_maxcdn_client_400_return_value
        })
        resp = controller_with_create_exception.create(
            service_name,
            service_json)
        self.assertIn('error', resp[driver.provider_name])

    @ddt.file_data('data_service.json')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_update(self, service_json):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_name = "test_service_name"
        resp = controller.update(service_name, service_json)
        self.assertIn('id', resp[new_driver.provider_name])

    @ddt.file_data('data_service.json')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_update_with_exception(self, service_json, mock_controllerclient,
                                   mock_driver):
        # test create with exceptions
        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'get.return_value':
                                        fake_maxcdn_client_get_return_value
                                        })

        service_name = "test_service_name"

        controller_with_update_exception = services.ServiceController(driver)
        controller_with_update_exception.client.configure_mock(**{
            "put.side_effect":
            RuntimeError('Updating service mysteriously failed.')})
        resp = controller_with_update_exception.update(
            service_name,
            service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller_with_update_exception.client.reset_mock()
        controller_with_update_exception.client.configure_mock(**{
            "put.side_effect": None,
            "put.return_value": fake_maxcdn_client_400_return_value
        })
        resp = controller_with_update_exception.update(
            service_name,
            service_json)
        self.assertIn('error', resp[driver.provider_name])

    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_delete(self):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_name = "test_service_name"
        resp = controller.delete(service_name)
        self.assertIn('id', resp[new_driver.provider_name])

    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_delete_with_exception(self, mock_controllerclient,
                                   mock_driver):
        # test create with exceptions
        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'get.return_value':
                                        fake_maxcdn_client_get_return_value
                                        })

        service_name = "test_service_name"

        controller_with_delete_exception = services.ServiceController(driver)
        controller_with_delete_exception.client.configure_mock(**{
            "delete.side_effect":
            RuntimeError('Deleting service mysteriously failed.')})
        resp = controller_with_delete_exception.delete(service_name)
        self.assertEqual(resp[driver.provider_name]['error'],
                         'failed to delete service')

        controller_with_delete_exception.client.reset_mock()
        controller_with_delete_exception.client.configure_mock(**{
            "delete.side_effect": None,
            "delete.return_value": fake_maxcdn_client_400_return_value
        })
        resp = controller_with_delete_exception.delete(service_name)
        self.assertEqual(resp[driver.provider_name]['error'],
                         'failed to delete service')
