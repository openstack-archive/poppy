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
import mock

from poppy.common import errors
from poppy.manager.base import providers
from tests.unit import base


@ddt.ddt
class TestProviderWrapper(base.TestCase):

    def setUp(self):
        super(TestProviderWrapper, self).setUp()
        self.provider_wrapper_obj = providers.ProviderWrapper()

    @ddt.file_data('data_provider_details.json')
    def test_update_with_keyerror(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="no_existent_provider")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.update,
                          mock_ext, provider_details_json, {})

    @ddt.file_data('data_provider_details_corrupted.json')
    def test_update_with_other_exception(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="Fastly")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.update,
                          mock_ext, provider_details_json, {})

    @ddt.file_data('data_provider_details.json')
    def test_update(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="Fastly",
                             obj=mock.Mock())
        fastly_provider_detail = json.loads(provider_details_json["Fastly"])
        self.provider_wrapper_obj.update(mock_ext,
                                         provider_details_json, {})
        mock_ext.obj.service_controller.update.assert_called_once_with(
            fastly_provider_detail['id'],
            {})

    @ddt.file_data('data_provider_details.json')
    def test_delete_with_keyerror(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="no_existent_provider")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.delete,
                          mock_ext, provider_details_json)

    @ddt.file_data('data_provider_details_corrupted.json')
    def test_delete_with_other_exception(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="Fastly")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.delete,
                          mock_ext, provider_details_json)

    @ddt.file_data('data_provider_details.json')
    def test_delete(self, provider_details_json):
        mock_ext = mock.Mock(provider_name="Fastly",
                             obj=mock.Mock())
        fastly_provider_detail = json.loads(provider_details_json["Fastly"])
        self.provider_wrapper_obj.delete(mock_ext, provider_details_json)
        mock_ext.obj.service_controller.delete.assert_called_once_with(
            fastly_provider_detail['id'])
