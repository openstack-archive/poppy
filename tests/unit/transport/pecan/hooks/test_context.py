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
import testtools

from oslo_context import context
from oslo_context import fixture
from webob.exc import HTTPClientError

from poppy.transport.pecan import hooks


class TestContextHook(testtools.TestCase):

    def setUp(self):
        super(TestContextHook, self).setUp()

        self.useFixture(fixture.ClearRequestContext())

        self.state = mock.Mock()
        self.state.controller.__self__ = mock.MagicMock(autospec=True)
        self.state.request = mock.Mock()
        self.state.request.headers = {}
        self.state.response.headers = {}
        self.state.request.environ = {}
        self.state.request.host_url = 'https://cdn.com'
        self.state.request.path = '/v1.0/endpoint'

        oslo_config_patcher = mock.patch('oslo_config.cfg.CONF')
        self.mock_cfg = oslo_config_patcher.start()
        self.mock_cfg.project_id_in_url = False
        self.addCleanup(oslo_config_patcher.stop)

        self.hook = hooks.context.ContextHook()

    def test_context_in_local_store(self):
        """Mocks Oslo local store to ensure the context is stored.

        This test exists to ensure we continue to populate a context in the
        Oslo local store, thus allowing Oslo log to pick it up.
        """
        tenant = '012345'
        self.state.request.headers['X-Project-ID'] = tenant

        self.hook.before(self.state)
        self.assertIsNotNone(context.get_current())
        self.assertIsInstance(
            context.get_current(), hooks.context.PoppyRequestContext
        )

    def test_x_project_id_header(self):
        tenant = '012345'
        self.state.request.headers['X-Project-ID'] = tenant

        self.hook.before(self.state)
        self.assertEqual(tenant, context.get_current().tenant)
        self.assertEqual(
            self.state.request.host_url + '/v1.0',
            context.get_current().base_url
        )

    def test_no_project_id(self):
        self.state.request.headers['X-Auth-Token'] = 'auth_token'
        self.assertRaises(HTTPClientError, self.hook.before, self.state)

    def test_tenant_id_url_with_header_and_injection(self):
        self.mock_cfg.project_id_in_url = True

        header_tenant = '012345'
        url_tenant = '567890'
        self.state.request.headers['X-Project-ID'] = header_tenant
        self.state.request.path = '/v1.0/' + url_tenant + '/services'

        self.hook.before(self.state)

        self.assertEqual(header_tenant, context.get_current().tenant)
        self.assertEqual(
            self.state.request.host_url + '/v1.0/' + header_tenant,
            context.get_current().base_url
        )
