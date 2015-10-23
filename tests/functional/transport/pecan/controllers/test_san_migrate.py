# Copyright (c) 2015 Rackspace, Inc.
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

from poppy.storage.mockdb.services import ServicesController
from tests.functional.transport.pecan import base


@ddt.ddt
class SanMigrationTest(base.FunctionalTest):

    def setUp(self):
        super(SanMigrationTest, self).setUp()

        self.project_id = str(uuid.uuid1())
        self.service_id = str(uuid.uuid1())
        self.flavor_id = str(uuid.uuid1())

    def test_migrate_san(self):

        san_migration_json = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'domain_name': 'www.myexampledomain.com',
            'new_cert': 'shiny_cert'
        }

        # create with good data
        with mock.patch.object(ServicesController, 'get_provider_details'):
            response = self.app.post('/v1.0/admin/provider/akamai/service',
                                     params=json.dumps(san_migration_json),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'X-Project-ID': self.project_id})
            self.assertEqual(202, response.status_code)

    @ddt.data('deployed', 'create_in_progress')
    def test_migrate_san_cert_status(self, cert_status):

        san_migration_json = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'domain_name': 'www.myexampledomain.com',
            'new_cert': 'shiny_cert',
            'cert_status': cert_status
        }

        # create with good data
        with mock.patch.object(ServicesController, 'get_provider_details'):
            response = self.app.post('/v1.0/admin/provider/akamai/service',
                                     params=json.dumps(san_migration_json),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'X-Project-ID': self.project_id})
            self.assertEqual(202, response.status_code)

    @ddt.data('scooby-doo', 'where are you?')
    def test_negative_migrate_san_cert_status(self, cert_status):

        san_migration_json = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'domain_name': 'www.myexampledomain.com',
            'new_cert': 'shiny_cert',
            'cert_status': cert_status
        }

        # create with good data

        response = self.app.post('/v1.0/admin/provider/akamai/service',
                                 params=json.dumps(san_migration_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def tearDown(self):
        super(SanMigrationTest, self).tearDown()
