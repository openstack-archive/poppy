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

import ddt
import mock

from poppy.model.helpers import domain
from poppy.provider.akamai import services
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch(
        'poppy.provider.akamai.services.ServiceController.policy_api_client')
    @mock.patch(
        'poppy.provider.akamai.services.ServiceController.ccu_api_client')
    @mock.patch('poppy.provider.akamai.driver.CDNProvider')
    def setUp(self, mock_controller_policy_api_client,
              mock_controller_ccu_api_client,
              mock_driver):
        super(TestServices, self).setUp()
        self.driver = mock_driver()
        self.driver.akamai_https_access_url_suffix = str(uuid.uuid1())
        self.controller = services.ServiceController(self.driver)

    @ddt.file_data('domains_list.json')
    def test_classify_domains(self, domains_list):
        domains_list = [domain.Domain(domain_s) for domain_s in domains_list]
        c_domains_list = self.controller._classify_domains(domains_list)
        self.assertEqual(domains_list, c_domains_list, 'Domain list not equal'
                         ' classified domain list')

    @ddt.file_data('data_service.json')
    def test_create_with_exception(self, service_json):
        # ASSERTIONS
        # create_service
        service_obj = service.load_from_json(service_json)

        self.controller.policy_api_client.put.side_effect = (
            RuntimeError('Creating service failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_4xx_return(self, service_json):
        service_obj = service.load_from_json(service_json)

        # test exception
        self.controller.policy_api_client.put.return_value = mock.Mock(
            status_code=400,
            text='Some create service error happened'
        )
        resp = self.controller.create(service_obj)

        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        service_obj = service.load_from_json(service_json)
        self.controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        self.controller.create(service_obj)
        self.controller.policy_api_client.put.assert_called_once()
        # make sure all the caching rules are processed
        self.assertTrue(service_obj.caching == [])

    def test_delete_with_exception(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])

        # test exception
        exception = RuntimeError('ding')
        self.controller.policy_api_client.delete.side_effect = exception
        resp = self.controller.delete(provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_service_id_json_load_error(self):
        # This should trigger a json.loads error
        provider_service_id = None
        resp = self.controller.delete(provider_service_id)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_4xx_return(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])

        # test exception
        self.controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=400,
            text='Some error happened'
        )
        resp = self.controller.delete(provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])

        self.controller.delete(provider_service_id)
        self.controller.policy_api_client.delete.assert_called_once()

    @ddt.file_data('data_update_service.json')
    def test_update_with_get_error(self, service_json):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)
        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=400,
            text='Some get error happened'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj, service_obj, service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update_with_service_id_json_load_error(self, service_json):
        # This should trigger a json.loads error
        provider_service_id = None
        service_obj = service.load_from_json(service_json)
        resp = self.controller.update(
            provider_service_id, service_obj, service_obj, service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update(self, service_json):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)
        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text=json.dumps(dict(rules=[]))
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj, service_obj, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update_with_domain_protocol_change(self, service_json):
        provider_service_id = json.dumps([{'policy_name': "densely.sage.com",
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)
        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text=json.dumps(dict(rules=[]))
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj, service_obj, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_purge_all(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)
        resp = controller.purge(provider_service_id, None)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge_with_service_id_json_load_error(self):
        provider_service_id = None
        controller = services.ServiceController(self.driver)
        resp = controller.purge(provider_service_id, None)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge_with_ccu_exception(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)
        controller.ccu_api_client.post.return_value = mock.Mock(
            status_code=400,
            text="purge request post failed"
        )
        resp = controller.purge(provider_service_id, '/img/abc.jpeg')
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'https'}])
        controller = services.ServiceController(self.driver)
        controller.ccu_api_client.post.return_value = mock.Mock(
            status_code=201,
            text="purge request post complete"
        )
        resp = controller.purge(provider_service_id, '/img/abc.jpeg')
        self.assertIn('id', resp[self.driver.provider_name])
