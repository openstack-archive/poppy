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

import os

import mock
from oslo_config import cfg

from poppy import bootstrap
from tests.unit import base


class TestBootStrap(base.TestCase):

    def test_boot_strap_successful(self):
        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(__file__)))
        conf_path = os.path.join(tests_path, 'etc', 'default_functional.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])

        bootstrap_obj = bootstrap.Bootstrap(cfg.CONF)

        mock_path = 'poppy.transport.pecan.driver.simple_server'
        with mock.patch(mock_path) as mocked_module:
            mock_server = mock.Mock()
            mocked_module.make_server = mock.Mock(return_value=mock_server)
            bootstrap_obj.run()
            self.assertTrue(mock_server.serve_forever.called)

    def test_boot_strap_when_exception(self):
        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(__file__)))
        conf_path = os.path.join(tests_path, 'etc', 'bootstrap_unit.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])

        bootstrap_obj = bootstrap.Bootstrap(cfg.CONF)

        self.assertTrue(bootstrap_obj.transport is None)
        self.assertTrue(bootstrap_obj.manager is None)
        self.assertTrue(bootstrap_obj.storage is None)
