# -*- coding: utf-8 -*-
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

import ddt

from poppy.model.helpers import provider_details
from tests.unit import base


@ddt.ddt
class TestProviderDetails(base.TestCase):

    def setUp(self):
        super(TestProviderDetails, self).setUp()
        self.my_provider_detail = provider_details.ProviderDetail()

    def test_provider_details(self):
        self.assertTrue(self.my_provider_detail.provider_service_id is None)
        self.assertTrue(self.my_provider_detail.access_urls == [])
        self.assertTrue(self.my_provider_detail.status == "deploy_in_progress")
        self.assertTrue(self.my_provider_detail.name is None)
        self.assertTrue(self.my_provider_detail.error_class is None)
        self.assertTrue(self.my_provider_detail.error_message is None)

    @ddt.data(u'deployed', u'create_in_progress', u'failed')
    def test_set_domain_certificate_status(self, status):
        self.my_provider_detail.domains_certificate_status.\
            set_domain_certificate_status("www.ab.com", status)

        self.assertTrue(
            self.my_provider_detail.domains_certificate_status.
            get_domain_certificate_status("www.ab.com") ==
            status)

    @ddt.data(u'invalid_status')
    def test_set_domain_certificate_status_invalid(self, status):
        self.assertRaises(
            ValueError,
            self.my_provider_detail.domains_certificate_status.
            set_domain_certificate_status,
            "www.ab.com",
            status)

    @ddt.data(u'deployed', u'create_in_progress', u'failed')
    def test_get_domain_certificate_status(self, status):
        current_status = (
            self.my_provider_detail.domains_certificate_status.
            get_domain_certificate_status("www.ab.com")
        )
        self.assertTrue(
            current_status, 'deployed')

        self.my_provider_detail.domains_certificate_status.\
            set_domain_certificate_status("www.ab.com", status)

        self.assertTrue(
            self.my_provider_detail.domains_certificate_status.
            get_domain_certificate_status("www.ab.com")
            == status)
