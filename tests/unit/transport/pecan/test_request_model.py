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

import ddt

from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestRequestsModel(base.TestCase):

    @ddt.file_data('data_service_model.json')
    def test_service_model(self, input_json):
        input_json = json.dumps(input_json)
        c = service.Model(input_json)

        self.assertTrue(isinstance(c.origins, list))
        self.assertTrue(isinstance(c.domains, list))
