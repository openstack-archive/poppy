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
from webob import exc

from poppy.common import errors
from poppy.transport.pecan import controllers
import poppy.transport.pecan.controllers.v1.admin
from tests.unit.transport.pecan.controllers import base


class DomainMigrationControllerTests(base.BasePecanControllerUnitTest):

    def setUp(self):
        super(DomainMigrationControllerTests, self).setUp(
            poppy.transport.pecan.controllers.v1.admin
        )

        self.controller = controllers.v1.admin.DomainMigrationController(
            self.driver
        )
        self.manager = self.driver.manager

    def test_migrate_domain_service_not_found(self):
        payload = {
            "project_id": "12345",
            "service_id": "abcdef",
            "domain_name": "www.mywebsite.com",
            "new_cert": "scdn1.secure6.raxcdn.com.edgekey.net",
            "cert_status": "create_in_progress"
        }
        self.request.body = bytearray(json.dumps(payload), encoding='utf-8')

        self.manager.services_controller.migrate_domain.side_effect = (
            errors.ServiceNotFound("Mock -- Couldn't find service!")
        )

        self.assertRaises(exc.HTTPNotFound, self.controller.post, payload)

    def test_migrate_domain_raises_value_error(self):
        payload = {
            "project_id": "12345",
            "service_id": "abcdef",
            "domain_name": "www.mywebsite.com",
            "new_cert": "scdn1.secure6.raxcdn.com.edgekey.net",
            "cert_status": "create_in_progress"
        }
        self.request.body = bytearray(json.dumps(payload), encoding='utf-8')

        self.manager.services_controller.migrate_domain.side_effect = (
            ValueError("Mock -- Couldn't find service provider details!")
        )

        self.assertRaises(exc.HTTPNotFound, self.controller.post, payload)


class BackgroundJobControllerTests(base.BasePecanControllerUnitTest):

    def setUp(self):
        super(BackgroundJobControllerTests, self).setUp(
            poppy.transport.pecan.controllers.v1.admin
        )

        self.controller = controllers.v1.admin.BackgroundJobController(
            self.driver
        )
        self.manager = self.driver.manager

    def test_background_job_not_implemented(self):
        payload = {
            "job_type": "not_implemented_job_type",
        }
        self.request.body = bytearray(json.dumps(payload), encoding='utf-8')

        self.manager.background_job_controller.post_job.side_effect = (
            NotImplementedError("Mock -- Job type not implemented!")
        )

        self.assertRaises(
            exc.HTTPClientError,
            self.controller.post,
            payload
        )
