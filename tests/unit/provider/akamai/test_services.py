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

import akamai
import ddt
import mock

from poppy.model.helpers import domain
from poppy.provider.akamai import services
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('poppy.provider.akamai.services.ServiceController.client')
    @mock.patch('poppy.provider.akamai.driver.CDNProvider')
    def setUp(self, mock_controllerclient, mock_driver):
        super(TestServices, self).setUp()
        self.driver = mock_driver()
        self.controller = services.ServiceController(self.driver)

    @ddt.file_data('domains_list.json')
    def test_classify_domains(self, domains_list):
        domains_list = [domain.Domain(domain_s) for domain_s in domains_list]
        c_domains_list = self.controller._classify_domains(domains_list)
        prev_content_realm = ''
        for c_domains in c_domains_list:
            self.assertTrue(len(c_domains) >= 1)
            content_realm = '.'.join(c_domains[0].split('.')[-2:])
            if len(c_domains) > 1:
                # inside a group the content realm should be
                # the same
                for c_domain in c_domains:
                    self.assertEqual(content_realm,
                                     '.'.join(c_domain.split('.')[-2:]))
            next_content_realm = content_realm
            # assert different group's content real is not eaual
            self.assertNotEqual(prev_content_realm, next_content_realm,
                                'classified domains\'s content realm'
                                ' should not equal')
            prev_content_realm = next_content_realm

    @ddt.file_data('data_service.json')
    def test_create_with_exception(self, service_json):
        # ASSERTIONS
        # create_service
        service_obj = service.load_from_json(service_json)

        self.controller.client.put.side_effect = (
            RuntimeError('Creating service failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_4xx_return(self, service_json):
        service_obj = service.load_from_json(service_json)

        # test exception
        self.controller.client.delete.return_value = mock.Mock(
            status_code=400,
            text='Some create service error happened'
        )
        resp = self.controller.create(service_obj)

        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        service_obj = service.load_from_json(service_json)
        self.controller.create(service_obj)

        self.controller.client.put.assert_called_once()

    def test_delete_with_exception(self):
        provider_service_id = json.dumps([str(uuid.uuid1())])

        # test exception
        exception = RuntimeError('ding')
        self.controller.client.delete.side_effect = exception
        resp = self.controller.delete(provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_service_id_json_load_error(self):
        # This should trigger a json.loads error
        provider_service_id = None
        resp = self.controller.delete(provider_service_id)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_4xx_return(self):
        provider_service_id = json.dumps([str(uuid.uuid1())])

        # test exception
        self.controller.client.delete.return_value = mock.Mock(
            status_code=400,
            text='Some error happened'
        )
        resp = self.controller.delete(provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
        provider_service_id = json.dumps([str(uuid.uuid1())])

        self.controller.delete(provider_service_id)
        self.controller.client.delete.assert_called_once()
