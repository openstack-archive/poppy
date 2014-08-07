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

from poppy.manager.default import v1

from tests.functional.transport.pecan import base


class V1ControllerTest(base.FunctionalTest):

    def test_get_all(self):
        response = self.app.get('/v1.0/00001')

        self.assertEqual(200, response.status_code)
        # Temporary until actual implementation
        self.assertEqual(v1.JSON_HOME, response.json)
