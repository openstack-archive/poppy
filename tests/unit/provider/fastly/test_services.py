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

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.service import Service
from poppy.provider.fastly import services
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('fastly.FastlyConnection')
    @mock.patch('fastly.FastlyService')
    @mock.patch('fastly.FastlyVersion')
    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def setUp(
        self,
        mock_driver,
        mock_controllerclient,
        mock_version,
        mock_service,
        mock_connection
    ):
        super(TestServices, self).setUp()
        self.driver = mock_driver()
        self.driver.provider_name = 'Fastly'
        self.driver.regions = []
        self.mock_service = mock_service
        self.mock_version = mock_version

        self.service_name = 'scarborough'
        mock_service_id = '%020x' % random.randrange(16 ** 20)
        self.mock_create_version_resp = {
            u'service_id': mock_service_id, u'number': 5}

        self.service_instance = self.mock_service()
        self.service_instance.id = mock_service_id
        self.controller = services.ServiceController(self.driver)
        self.version = self.mock_version(
            self.controller.client,
            self.mock_create_version_resp)
        self.version.number = self.mock_create_version_resp.get('number')
        self.controller.client.create_service.return_value = (
            self.service_instance)
        self.controller.client.create_version.return_value = self.version

    @ddt.file_data('data_service.json')
    def test_create_with_create_service_exception(self, service_json):
        # ASSERTIONS
        # create_service
        service_obj = service.load_from_json(service_json)

        self.controller.client.create_service.side_effect = fastly.FastlyError(
            Exception('Creating service failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_create_version_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_service.side_effect = None
        service_obj = service.load_from_json(service_json)

        # create_version
        self.controller.client.create_version.side_effect = fastly.FastlyError(
            Exception('Creating version failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_create_domain_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_version.side_effect = None
        service_obj = service.load_from_json(service_json)

        # create domains
        self.controller.client.create_domain.side_effect = fastly.FastlyError(
            Exception('Creating domains failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_create_backend_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_domain.side_effect = None
        service_obj = service.load_from_json(service_json)

        # create backends
        self.controller.client.create_backend.side_effect = fastly.FastlyError(
            Exception('Creating backend failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_check_domains_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_backend.side_effect = None
        service_obj = service.load_from_json(service_json)

        self.controller.client.check_domains.side_effect = fastly.FastlyError(
            Exception('Check_domains failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_list_versions_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_backend.side_effect = None
        service_obj = service.load_from_json(service_json)

        self.controller.client.list_versions.side_effect = fastly.FastlyError(
            Exception('List_versions failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_activate_version_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.create_backend.side_effect = None
        service_obj = service.load_from_json(service_json)

        self.controller.client.active_version.side_effect = fastly.FastlyError(
            Exception('Active_version failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_general_exception(self, service_json):
        self.controller.client.reset_mock()
        self.controller.client.check_domains.side_effect = None
        service_obj = service.load_from_json(service_json)

        # test a general exception
        self.controller.client.create_service.side_effect = Exception(
            'Wild exception occurred.')
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service_no_restrictions.json')
    def test_create_with_no_restriction(self, service_json):
        # instantiate
        # this case needs to set all return value for each call
        service_obj = service.load_from_json(service_json)

        controller = services.ServiceController(self.driver)

        controller.client.create_service.return_value = self.service_instance
        controller.client.create_version.return_value = self.version
        controller.client.list_versions.return_value = [self.version]
        controller.client.active_version.return_value = self.version

        fastly_fake_domain_check = type(
            'FastlyDomain', (object,), {
                'name': 'fake_domain.global.prod.fastly.net'})
        controller.client.check_domains.return_value = [
            mock.Mock(domain=fastly_fake_domain_check)
        ]

        resp = controller.create(service_obj)

        controller.client.create_service.assert_called_once_with(
            controller.current_customer.id, service_obj.name)

        controller.client.create_version.assert_called_once_with(
            self.service_instance.id)

        controller.client.create_domain.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.domains[0].domain)

        controller.client.create_domain.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.domains[1].domain)

        controller.client.check_domains.assert_called_once_with(
            self.service_instance.id, self.version.number)

        self.assertEqual(False, controller.client.create_condition.called)
        self.assertEqual(False,
                         controller.client.create_response_object.called)

        controller.client.create_backend.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.origins[0].origin.replace(":", "-"),
            service_obj.origins[0].origin,
            service_obj.origins[0].ssl,
            service_obj.origins[0].port)

        self.assertIn('links', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        # instantiate
        # this case needs to set all return value for each call
        service_obj = service.load_from_json(service_json)

        controller = services.ServiceController(self.driver)

        controller.client.create_service.return_value = self.service_instance
        controller.client.create_version.return_value = self.version
        controller.client.list_versions.return_value = [self.version]
        controller.client.active_version.return_value = self.version

        fastly_fake_domain_check = type(
            'FastlyDomain', (object,), {
                'name': 'fake_domain.global.prod.fastly.net'})
        controller.client.check_domains.return_value = [
            mock.Mock(domain=fastly_fake_domain_check)
        ]

        resp = controller.create(service_obj)

        controller.client.create_service.assert_called_once_with(
            controller.current_customer.id, service_obj.name)

        controller.client.create_version.assert_called_once_with(
            self.service_instance.id)

        controller.client.create_domain.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.domains[0].domain)

        controller.client.create_domain.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.domains[1].domain)

        controller.client.check_domains.assert_called_once_with(
            self.service_instance.id, self.version.number)

        referrer_restriction_list = [rule.referrer
                                     for restriction in
                                     service_obj.restrictions
                                     for rule in restriction.rules
                                     if hasattr(rule, 'referrer')]

        # referrer assert
        host_pattern_statement = ' || '.join(['req.http.referer'
                                              ' !~ "%s"' % host for host in
                                              referrer_restriction_list
                                              if host is not None])
        condition_stmt = ('req.http.referer && (%s)'
                          % host_pattern_statement)

        controller.client.create_condition.assert_any_call(
            self.service_instance.id,
            self.version.number,
            'Referrer Restriction Matching Rules',
            fastly.FastlyConditionType.REQUEST,
            condition_stmt,
            priority=10)

        controller.client.create_response_object.assert_any_call(
            self.service_instance.id,
            self.version.number,
            'Referrer Restriction response rule(s)',
            content='Referring from a non-permitted domain',
            status='403',
            request_condition=controller.client.create_condition().name
        )

        # cache rule asset
        # create condition first
        for caching_rule in service_obj.caching:
            if caching_rule.name.lower() == 'default':
                controller.client.update_settings.assert_called_once_with(
                    self.service_instance.id,
                    self.version.number,
                    {'general.default_ttl': caching_rule.ttl}
                )
            else:

                controller.client.create_cache_settings.assert_any_call(
                    self.service_instance.id,
                    self.version.number,
                    caching_rule.name,
                    None,
                    cache_condition=controller.client.create_condition().name,
                    stale_ttl=0,
                    ttl=caching_rule.ttl
                )

        controller.client.create_backend.assert_any_call(
            self.service_instance.id,
            self.version.number,
            service_obj.origins[0].origin.replace(":", "-"),
            service_obj.origins[0].origin,
            service_obj.origins[0].ssl,
            service_obj.origins[0].port)

        self.assertIn('links', resp[self.driver.provider_name])

    def test_delete_with_exception(self):
        provider_service_id = uuid.uuid1()

        # instantiate
        controller = services.ServiceController(self.driver)

        # mock.patch return values
        service = self.mock_service()
        service.id = uuid.uuid1()
        controller.client.get_service_by_name.return_value = service

        # test exception
        controller.client.delete_service.side_effect = None
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

        exception = fastly.FastlyError(Exception('ding'))
        controller.client.delete_service.side_effect = exception
        resp = controller.delete(service_obj, provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
        provider_service_id = uuid.uuid1()

        # instantiate
        controller = services.ServiceController(self.driver)

        # clear run
        controller.client.delete_service.side_effect = None
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
        resp = controller.delete(service_obj, provider_service_id)
        controller.client.delete_service.assert_called_once_with(
            provider_service_id)
        self.assertIn('id', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_update(self, service_json):
        provider_service_id = uuid.uuid1()
        controller = services.ServiceController(self.driver)
        controller.client.list_versions.return_value = [self.version]
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_purge_with_exception(self):
        provider_service_id = uuid.uuid1()
        controller = services.ServiceController(self.driver)
        exception = fastly.FastlyError(Exception('ding'))
        controller.client.purge_service.side_effect = exception
        resp = controller.purge(provider_service_id, hard=True,
                                purge_url='/*')
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge_all(self):
        provider_service_id = uuid.uuid1()
        controller = services.ServiceController(self.driver)
        controller.client.purge_service.return_value = 'some_value'
        resp = controller.purge(provider_service_id, hard=True,
                                purge_url='/*')
        controller.client.purge_service.assert_called_once_with(
            provider_service_id
        )
        self.assertIn('id', resp[self.driver.provider_name])

    def test_purge_partial(self):
        provider_service_id = uuid.uuid1()
        controller = services.ServiceController(self.driver)
        controller.client.purge_service.return_value = 'some_value'
        controller.client.list_domains.return_value = [
            mock.Mock(name='domain_1'),
            mock.Mock(name='domain_2')]
        controller.client.purge_url.return_value = 'purge_url_return'
        resp = controller.purge(provider_service_id, ['/url_1', '/url_2'])
        self.assertIn('id', resp[self.driver.provider_name])

    def test_client(self):
        controller = services.ServiceController(self.driver)
        self.assertNotEqual(controller.client(), None)


class TestProviderValidation(base.TestCase):

    """Tests for provider side validation methods.

    This class tests the validation methods to verify the data accuracy
    at the provider side.
    """

    @mock.patch('poppy.provider.fastly.services.ServiceController.client')
    @mock.patch('poppy.provider.fastly.driver.CDNProvider')
    def setUp(self, mock_driver, mock_client):
        super(TestProviderValidation, self).setUp()

        self.driver = mock_driver()
        self.controller = services.ServiceController(self.driver)
        self.client = mock_client
        self.service_name = uuid.uuid1()
        service_json = {"name": "mocksite.com",
                        "domains": [{"domain": "parsely.sage.com"}],
                        "origins": [{"origin": "mockdomain.com",
                                     "ssl": False, "port": 80}],
                        "flavor_id": "standard"}
        service_obj = service.load_from_json(service_json)
        self.controller.create(service_obj)

    @mock.patch('fastly.FastlyService')
    def test_get_service_details(self, mock_service):

        service = mock_service()
        service.id = uuid.uuid1()
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
        resp = self.controller.get('error-service')

        self.assertIn('error', resp[self.driver.provider_name])

    def test_get_service_details_exception(self):
        exception = Exception('DOOM')
        self.controller.client.get_service_by_name.side_effect = exception
        resp = self.controller.get('magic-service')

        self.assertIn('error', resp[self.driver.provider_name])

    def test_regions(self):
        driver = mock.Mock()
        driver.regions = []
        controller = services.ServiceController(driver)
        self.assertEqual(controller.driver.regions, [])
