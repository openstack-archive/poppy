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

from oslo_config import cfg

from poppy import bootstrap
from poppy.manager.default import flavors
from poppy.manager.default import health
from poppy.manager.default import services
from tests.unit import base


class DefaultManagerDriverTests(base.TestCase):

    def setUp(self):
        super(DefaultManagerDriverTests, self).setUp()

        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))))
        conf_path = os.path.join(tests_path, 'etc', 'default_functional.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])

        self.bootstrapper = bootstrap.Bootstrap(cfg.CONF)
        self.driver = self.bootstrapper.manager
        self.mock_provider = self.bootstrapper.provider['mock']
        self.mock_storage = self.bootstrapper.storage

    def test_services_controller(self):
        sc = self.driver.services_controller

        self.assertIsInstance(sc, services.DefaultServicesController)

    def test_flavors_controller(self):
        fc = self.driver.flavors_controller

        self.assertIsInstance(fc, flavors.DefaultFlavorsController)

    def test_health_controller(self):
        hc = self.driver.health_controller

        self.assertIsInstance(hc, health.DefaultHealthController)
