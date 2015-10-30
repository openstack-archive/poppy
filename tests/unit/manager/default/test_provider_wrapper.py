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

import mock

from poppy.common import errors
from poppy.manager.base import providers
from poppy.model.helpers import provider_details
from tests.unit import base


class TestProviderWrapper(base.TestCase):

    def setUp(self):
        super(TestProviderWrapper, self).setUp()
        self.provider_wrapper_obj = providers.ProviderWrapper()
        # fake a provider details to work with unittest
        self.fake_provider_details = {
            "Fastly": provider_details.ProviderDetail(
                provider_service_id=uuid.uuid1(),
                access_urls=['mydummywebsite.prod.fastly.com'])}

    def test_update_with_keyerror(self):
        mock_ext = mock.Mock(provider_name="no_existent_provider")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.update,
                          mock_ext, self.fake_provider_details, {})

    def test_update(self):
        mock_obj = mock.Mock(provider_name='Fastly')
        mock_ext = mock.Mock(obj=mock_obj)
        fastly_provider_detail = self.fake_provider_details['Fastly']
        self.provider_wrapper_obj.update(mock_ext,
                                         self.fake_provider_details,
                                         {})
        mock_ext.obj.service_controller.update.assert_called_once_with(
            fastly_provider_detail.provider_service_id, {})

    def test_delete_with_keyerror(self):
        mock_ext = mock.Mock(obj=mock.Mock(
            provider_name="no_existent_provider"))
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.delete,
                          mock_ext, self.fake_provider_details,
                          str(uuid.uuid4()))

    def test_delete(self):
        mock_ext = mock.Mock(obj=mock.Mock(provider_name="Fastly"))
        fastly_provider_detail = self.fake_provider_details["Fastly"]
        fake_project_id = str(uuid.uuid4())
        self.provider_wrapper_obj.delete(mock_ext,
                                         self.fake_provider_details,
                                         fake_project_id)
        mock_ext.obj.service_controller.delete.assert_called_once_with(
            fake_project_id,
            fastly_provider_detail.provider_service_id,)

    def test_purge_with_keyerror(self):
        mock_ext = mock.Mock(provider_name="no_existent_provider")
        self.assertRaises(errors.BadProviderDetail,
                          self.provider_wrapper_obj.purge,
                          mock_ext, None, self.fake_provider_details)

    def test_purge(self):
        mock_ext = mock.Mock(obj=mock.Mock(provider_name="Fastly"))
        fastly_provider_detail = self.fake_provider_details["Fastly"]
        self.provider_wrapper_obj.purge(mock_ext, None,
                                        self.fake_provider_details,
                                        False,
                                        None)
        mock_ext.obj.service_controller.purge.assert_called_once_with(
            fastly_provider_detail.provider_service_id, None, False, None)
