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
from oslo_context import context as context_utils
import six.moves as sm
import testtools

from poppy.transport.pecan import controllers
from poppy.transport.pecan.controllers import v1
from poppy.transport.validators import helpers


class BasePecanControllerUnitTest(testtools.TestCase):

    def setUp(self, controller):
        """Engages all patches for unit testing controllers.

        Patches the request, response, request context, and deserialization
        decorator to satisfy all controller dependencies for unit testing.

        :returns: None
        """

        super(BasePecanControllerUnitTest, self).setUp()

        self.addCleanup(
            sm.reload_module,
            controllers
        )
        self.addCleanup(
            sm.reload_module,
            v1
        )
        self.addCleanup(
            sm.reload_module,
            controller
        )
        self.addCleanup(
            sm.reload_module,
            context_utils
        )
        self.addCleanup(
            sm.reload_module,
            helpers
        )

        self.driver = mock.MagicMock()
        self.response = mock.Mock()

        context = mock.Mock()
        context.tenant = '000000001'
        context.user = 'user_id'
        context_utils.get_current = context
        context_utils.get_current.return_value = context

        pecan_request_patcher = mock.patch('pecan.request')
        self.request = pecan_request_patcher.start()
        self.request.host_url = 'test_url'
        self.request.base_url = 'test_url'

        pecan_response_patcher = mock.patch('pecan.response')
        self.response = pecan_response_patcher.start()
        self.response.headers = {}

        deco_patcher = mock.patch('poppy.transport.validators.helpers')
        deco_patcher.start()

        # Reload to engage patches
        sm.reload_module(controller)
        sm.reload_module(v1)
        sm.reload_module(controllers)
        sm.reload_module(helpers)

        # self.addCleanup(deco_patcher.stop)
        self.addCleanup(deco_patcher.stop)
        self.addCleanup(pecan_response_patcher.stop)
        self.addCleanup(pecan_request_patcher.stop)
