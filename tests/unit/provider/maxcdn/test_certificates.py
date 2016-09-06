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

import mock

from poppy.provider.maxcdn import certificates

from tests.unit import base


class TestCertificates(base.TestCase):

    def setUp(self):
        super(TestCertificates, self).setUp()
        self.driver = mock.Mock()
        self.driver.provider_name = 'Maxcdn'

        self.controller = certificates.CertificateController(self.driver)

    def test_create_certificate(self):
        self.assertEqual(
            NotImplemented, self.controller.create_certificate({}))
