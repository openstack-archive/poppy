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

from tests.api import base
from tests.api.utils import config
from tests.api.utils import fastlyclient as fastly


class TestProviderBase(base.TestBase):
    """Child class of base.TestBase for validating provider updates.

    Inherit from this and write your test methods (for tests that require
    provider side validation. Operators might need to add validation for
    providers not supported already.If the child class defines a prepare(self)
    method, this method will be called before executing each test method.
    """

    @classmethod
    def setUpClass(cls):
        super(TestProviderBase, cls).setUpClass()

    def getServiceFromProvider(self, provider, service_name):
        if provider == 'fastly':
            fastly_config = config.FastlyConfig()
            fastly_client = fastly.FastlyClient(
                api_key=fastly_config.api_key,
                email=fastly_config.email,
                password=fastly_config.password)
            service_details = fastly_client.get_service(service_name)
        return service_details

    def getServiceFromFlavor(self, flavor, service_name):
        """Verify response schema aligns with the expected schema."""
        provider_list = self.config.flavor[flavor]
        service_details = dict(
            (provider, self.getServiceFromProvider(provider, service_name))
            for provider in provider_list)
        return service_details

    @classmethod
    def tearDownClass(cls):
        super(TestProviderBase, cls).tearDownClass()
