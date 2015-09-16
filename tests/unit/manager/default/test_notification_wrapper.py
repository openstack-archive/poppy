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

import mock

from poppy.manager.base import notifications
from tests.unit import base


class TestProviderWrapper(base.TestCase):

    def setUp(self):
        super(TestProviderWrapper, self).setUp()
        self.notifications_wrapper_obj = notifications.NotificationWrapper()

    def test_create(self):
        mock_obj = mock.Mock()
        mock_ext = mock.Mock(obj=mock_obj)
        self.notifications_wrapper_obj.send(mock_ext,
                                            "test_subject",
                                            "test_mail_content")

        mock_ext.obj.services_controller.send.assert_called_once_with(
            "test_subject", "test_mail_content")
