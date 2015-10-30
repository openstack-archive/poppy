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

from boto import cloudfront
import ddt
import mock

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.service import Service
from poppy.provider.cloudfront import services
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('poppy.provider.cloudfront.services.ServiceController.client')
    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    def setUp(self, mock_get_client, MockDriver):
        super(TestServices, self).setUp()

        self.service_name = uuid.uuid1()
        self.provider_service_id = uuid.uuid1()
        self.mock_get_client = mock_get_client
        self.driver = MockDriver()
        self.driver.regions = []
        self.controller = services.ServiceController(self.driver)

    def test_get(self):
        resp = self.controller.get(self.service_name)
        self.assertIn('domains', resp)
        self.assertIn('origins', resp)
        self.assertIn('caching', resp)

    @ddt.file_data('data_service.json')
    def test_create_server_error(self, service_json):
        # create_distribution: CloudFrontServerError
        service_obj = service.load_from_json(service_json)
        side_effect = cloudfront.exception.CloudFrontServerError(
            503, 'Service Unavailable')
        self.controller.client.create_distribution.side_effect = side_effect

        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_exception(self, service_json):
        # generic exception: Exception
        service_obj = service.load_from_json(service_json)
        self.controller.client.create_distribution.side_effect = Exception(
            'Creating service failed.')
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_service_in_progress(self, service_json):
        # clear run
        service_obj = service.load_from_json(service_json)
        self.controller.client.create_distribution.return_value = (
            mock.Mock(domain_name="jibberish.cloudfront.com",
                      id=uuid.uuid1(),
                      status="InProgress")
        )
        resp = self.controller.create(service_obj)
        self.assertIn('links', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_service_deployed(self, service_json):
        # clear run
        service_obj = service.load_from_json(service_json)
        self.controller.client.create_distribution.return_value = (
            mock.Mock(domain_name="jibberish.cloudfront.com",
                      id=uuid.uuid1(),
                      status="Deployed")
        )
        resp = self.controller.create(service_obj)
        self.assertIn('links', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_service_unknown(self, service_json):
        # clear run
        service_obj = service.load_from_json(service_json)
        resp = self.controller.create(service_obj)
        self.assertIn('links', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_update(self, service_json):
        service_obj = service.load_from_json(service_json)
        resp = self.controller.update(self.provider_service_id,
                                      service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_delete_exceptions(self):
        # delete_distribution: Exception
        self.controller.client.delete_distribution.side_effect = Exception(
            'Deleting service failed.')
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
        resp = self.controller.delete(project_id=service_obj.project_id,
                                      service_name=self.service_name)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
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
        resp = self.controller.delete(project_id=service_obj.project_id,
                                      service_name=self.service_name)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_purge_exceptions(self):
        self.controller.client.create_invalidation_request.side_effect = (
            Exception('Purging service failed.')
        )
        resp = self.controller.purge(self.service_name)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge(self):
        resp = self.controller.purge(self.service_name)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_client(self):
        self.assertNotEqual(self.controller.client(), None)

    def test_current_customer(self):
        # TODO(tonytan4ever/obulpathi): fill in once correct
        # current_customer logic is done
        self.assertTrue(self.controller.current_customer is None)

    def test_regions(self):
        self.assertEqual(self.controller.driver.regions, [])
