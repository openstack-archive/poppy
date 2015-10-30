# -*- coding: utf-8 -*-
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

import ddt
import mock
from oslo_config import cfg

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.service import Service
from poppy.provider.maxcdn import driver
from poppy.provider.maxcdn import services
from poppy.transport.pecan.models.request import service
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


fake_maxcdn_client_get_return_value = {u'code': 200,
                                       u'data':
                                       {u'account':
                                        {u'status': u'2',
                                         u'name': u'<My_fake_company_alias>',
                                         u'id': u'32811'
                                         }}}

fake_maxcdn_client_400_return_value = {
    u'code': 400,
    u'message': 'operation PUT/GET/POST failed due to technical difficulties..'
}


class fake_maxcdn_api_client(object):

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
                    u'pullzone': {
                        u'cdn_url': u'newpullzone1.alias.netdna-cdn.com',
                        u'name': u'newpullzone1',
                        u'id': u'97312'
                    }}}

    def put(self, url=None, params=None):
        return {u'code': 200,
                u'data': {
                    u'pullzone': {
                        u'cdn_url': u'newpullzone1.alias.netdna-cdn.com',
                        u'name': u'newpullzone1',
                        u'id': u'97312'
                    }}}

    def delete(self, url=None):
        return {u'code': 200,
                }


@ddt.ddt
class TestServices(base.TestCase):

    def setUp(self):
        super(TestServices, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.provider_service_id = uuid.uuid1()

    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_get(self):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        service_name = 'test_service_name'
        self.assertTrue(controller.get(service_name) is not None)

    @ddt.file_data('data_service.json')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_create(self, service_json):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_obj = service.load_from_json(service_json)
        resp = controller.create(service_obj)
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
        service_obj = service.load_from_json(service_json)

        controller_with_create_exception = services.ServiceController(driver)
        controller_with_create_exception.client.configure_mock(**{
            'post.side_effect':
            RuntimeError('Creating service mysteriously failed.')})
        resp = controller_with_create_exception.create(
            service_obj)
        self.assertIn('error', resp[driver.provider_name])

        controller_with_create_exception.client.reset_mock()
        controller_with_create_exception.client.configure_mock(**{
            'post.side_effect': None,
            'post.return_value': fake_maxcdn_client_400_return_value
        })
        resp = controller_with_create_exception.create(
            service_obj)
        self.assertIn('error', resp[driver.provider_name])

    @ddt.file_data('data_service.json')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_update(self, service_json):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_obj = service.load_from_json(service_json)
        resp = controller.update(self.provider_service_id,
                                 service_obj)
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

        controller_with_update_exception = services.ServiceController(driver)
        controller_with_update_exception.client.configure_mock(**{
            'put.side_effect':
            RuntimeError('Updating service mysteriously failed.')})
        resp = controller_with_update_exception.update(
            self.provider_service_id,
            service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller_with_update_exception.client.reset_mock()
        controller_with_update_exception.client.configure_mock(**{
            'put.side_effect': None,
            'put.return_value': fake_maxcdn_client_400_return_value
        })
        service_obj = service.load_from_json(service_json)
        resp = controller_with_update_exception.update(
            self.provider_service_id,
            service_obj)
        self.assertIn('error', resp[driver.provider_name])

    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_delete(self):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        # test create, everything goes through successfully
        service_name = 'test_service_name'
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))
        resp = controller.delete(service_obj, service_name)
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

        service_name = 'test_service_name'

        controller_with_delete_exception = services.ServiceController(driver)
        controller_with_delete_exception.client.configure_mock(**{
            'delete.side_effect':
            RuntimeError('Deleting service mysteriously failed.')})
        service_name = 'test_service_name'
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))
        resp = controller_with_delete_exception.delete(service_obj,
                                                       service_name)
        self.assertEqual(resp[driver.provider_name]['error'],
                         'Deleting service mysteriously failed.')

    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_purge_with_exception(self, mock_controllerclient, mock_driver):
        # test create with exceptions
        error_message = "ding"

        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'purge.side_effect':
                                        RuntimeError(error_message)
                                        })
        controller_purge_with_error = services.ServiceController(driver)
        pullzone_id = 'test_random_pullzone_id'
        resp = controller_purge_with_error.purge(pullzone_id)
        self.assertEqual(resp[driver.provider_name]['error'],
                         error_message)

    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_purge(self, mock_controllerclient, mock_driver):
        # test create with exceptions
        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'purge.return_value':
                                        {u'code': 200}
                                        })
        controller_purge_with_error = services.ServiceController(driver)
        pullzone_id = 'test_random_pullzone_id'
        resp = controller_purge_with_error.purge(pullzone_id)
        self.assertIn('id', resp[driver.provider_name])

    @ddt.data('good-service-name', 'yahooservice')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_map_service_name_no_hash(self, service_name):
        maxcdn_driver = driver.CDNProvider(self.conf)
        controller = services.ServiceController(maxcdn_driver)
        self.assertEqual(controller._map_service_name(service_name),
                         service_name)

    @ddt.data(u'www.düsseldorf-Lörick.com', 'yahoo%_notvalid')
    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_map_service_name_with_hash(self, service_name):
        maxcdn_driver = driver.CDNProvider(self.conf)
        controller = services.ServiceController(maxcdn_driver)
        # test hashed
        self.assertNotEqual(controller._map_service_name(service_name),
                            service_name)
        # test deterministic-ity
        self.assertEqual(controller._map_service_name(service_name),
                         controller._map_service_name(service_name))

    @mock.patch.object(driver.CDNProvider, 'client',
                       new=fake_maxcdn_api_client())
    def test_current_customer(self):
        new_driver = driver.CDNProvider(self.conf)
        # instantiate
        controller = services.ServiceController(new_driver)
        self.assertTrue(controller.current_customer['name'] ==
                        u'<My_fake_company_alias>')

    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_current_customer_error(self, mock_controllerclient, mock_driver):
        # test create with exceptions
        driver = mock_driver()
        driver.attach_mock(mock_controllerclient, 'client')
        driver.client.configure_mock(**{'get.return_value':
                                        fake_maxcdn_client_400_return_value
                                        })

        controller = services.ServiceController(mock_driver)
        # for some reason self.assertRaises doesn't work
        try:
            controller.current_customer
        except RuntimeError as e:
            self.assertTrue(str(e) == "Get maxcdn current customer failed...")

    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider.client')
    @mock.patch('poppy.provider.maxcdn.driver.CDNProvider')
    def test_regions(self, mock_controllerclient, mock_driver):
        driver = mock_driver()
        driver.regions = []
        driver.attach_mock(mock_controllerclient, 'client')
        controller = services.ServiceController(driver)
        self.assertEqual(controller.driver.regions, [])
