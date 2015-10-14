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

import mock

from poppy.manager.default.services import DefaultServicesController
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model import service
from tests.functional.transport.pecan import base


class TestServicesAction(base.FunctionalTest):

    def test_services_action_with_bad_input(self):
        # missing action field
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1())
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 }, expect_errors=True)

        self.assertEqual(response.status_code, 400)

    def test_services_action_enable(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'action': 'enable'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 })

        self.assertEqual(response.status_code, 202)

    def test_services_action_disable(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'action': 'disable'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 })

        self.assertEqual(response.status_code, 202)

    def test_services_action_delete(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'project_id': str(uuid.uuid1()),
                                     'action': 'delete'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 })

        self.assertEqual(response.status_code, 202)

    def test_services_action_with_domain_existing_domain(self):
        project_id = str(uuid.uuid4())
        service_id = str(uuid.uuid4())
        domains = domain.Domain(domain='happy.strawberries.com')
        current_origin = origin.Origin(origin='poppy.org')
        mock_service = service.Service(service_id=service_id,
                                       name='poppy cdn service',
                                       domains=[domains],
                                       origins=[current_origin],
                                       flavor_id='cdn',
                                       project_id=project_id)

        DefaultServicesController.get_service_by_domain_name = mock.Mock(
            return_value=mock_service
        )
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'action': 'enable',
                                     'domain': 'happy.strawberries.com'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': project_id
                                 },
                                 expect_errors=True)

        self.assertEqual(response.status_code, 202)

    def test_services_action_with_domain_non_existing_domain(self):
        project_id = str(uuid.uuid4())

        DefaultServicesController.get_service_by_domain_name = mock.Mock(
            side_effect=ValueError
        )
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'action': 'enable',
                                     'domain': 'sad.strawberries.com'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': project_id
                                 },
                                 expect_errors=True)

        self.assertEqual(response.status_code, 404)

    def test_services_action_with_domain_existing_domain_and_project_id(self):
        project_id = str(uuid.uuid4())

        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'action': 'enable',
                                     'domain': 'sad.strawberries.com',
                                     'project_id': project_id
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': project_id
                                 },
                                 expect_errors=True)

        self.assertEqual(response.status_code, 400)

    def test_services_action_with_domain_and_no_actions(self):
        response = self.app.post('/v1.0/admin/services/action',
                                 params=json.dumps({
                                     'domain': 'sad.strawberries.com'
                                 }),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': str(uuid.uuid1())
                                 },
                                 expect_errors=True)

        self.assertEqual(response.status_code, 400)
