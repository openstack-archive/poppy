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

import mock
import pecan
import webtest

from poppy.transport.pecan import controllers
from poppy.transport.pecan.controllers import v1
from tests.unit import base


class TestHealth(base.TestCase):

    @mock.patch('poppy.transport.pecan.driver.PecanTransportDriver')
    @mock.patch('poppy.manager.default.driver.DefaultManagerDriver')
    def setUp(self, MockPecanTransportDriver, MockDefaultManagerDriver):
        super(TestHealth, self).setUp()

        conf = 'conf'
        storage = 'storage'
        providers = 'providers'
        self.mock_manager = MockDefaultManagerDriver(conf, storage, providers)
        self.mock_pecan_transport_driver = MockPecanTransportDriver(
            conf, self.mock_manager)

        setattr(self.mock_pecan_transport_driver, 'manager', self.mock_manager)

        root_controller = controllers.Root(self.mock_pecan_transport_driver)
        home_controller = v1.Home(self.mock_pecan_transport_driver)
        root_controller.add_controller('v1.0', home_controller)
        health_controller = v1.Health(
            self.mock_pecan_transport_driver)
        setattr(health_controller, '_driver', self.mock_pecan_transport_driver)
        home_controller.add_controller('health', health_controller)
        self.health_controller = health_controller
        self.wsgi_app = pecan.make_app(root_controller)
        self.app = webtest.TestApp(self.wsgi_app)

    def test_get_health_storage_not_available(self):
        self.mock_manager.health_storage = mock.MagicMock(
            return_value=('cassandra', False))
        response = self.app.get('/v1.0/health', expect_errors=True)
        self.assertEqual(response.status_code, 503)

    def test_get_storage_not_available(self):
        self.mock_manager.health_storage = mock.MagicMock(
            return_value=('cassandra', False))
        response = self.app.get('/v1.0/health/storage', expect_errors=True)
        self.assertEqual(response.status_code, 503)

    def test_get_health_provider_not_available(self):
        self.mock_manager.health_storage = mock.MagicMock(
            return_value=('cassandra', True))
        self.mock_manager.health_providers = mock.MagicMock(
            return_value=[('fastly', False)])
        response = self.app.get('/v1.0/health', expect_errors=True)
        self.assertEqual(response.status_code, 503)

    def test_get_provider_not_available(self):
        self.mock_manager.health_provider = mock.MagicMock(
            return_value=('fastly', False))
        response = self.app.get('/v1.0/health/fastly', expect_errors=True)
        self.assertEqual(response.status_code, 503)

    def test_get_unkown_provider(self):
        self.mock_manager.health_provider = mock.Mock(
            side_effect=KeyError('unknown'))
        response = self.app.get('/v1.0/health/unknown', expect_errors=True)
        self.assertEqual(response.status_code, 204)
