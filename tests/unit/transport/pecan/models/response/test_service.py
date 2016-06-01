# Copyright (c) 2016 Rackspace, Inc.
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

import ddt
import mock

from poppy.model import service as model_service
from poppy.transport.pecan.models.response import service as resp_model
from tests.unit import base


@ddt.ddt
class TestServiceResponseModel(base.TestCase):

    def setUp(self):
        super(TestServiceResponseModel, self).setUp()

        self.controller = mock.Mock()
        self.controller.base_url = "http://mock.base.url"

    @ddt.file_data('data_service_resp_model.json')
    def test_service_response_model(self, service_json):
        service_obj = model_service.Service.init_from_dict('000', service_json)

        service_model = resp_model.Model(service_obj, self.controller)
        self.assertEqual(service_json["name"], service_model['name'])
