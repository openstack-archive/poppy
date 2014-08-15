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

import ddt

from poppy.model import flavor
from tests.unit import base


@ddt.ddt
class TestFlavorModel(base.TestCase):

    def setUp(self):
        super(TestFlavorModel, self).setUp()

    def test_create_with_providers(self):
        self.flavor_id = uuid.uuid1()
        self.providers = []

        self.providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))
        self.providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))
        self.providers.append(flavor.Provider(uuid.uuid1(), uuid.uuid1()))

        my_flavor = flavor.Flavor(self.flavor_id, self.providers)

        # test all properties
        self.assertEqual(my_flavor.flavor_id, self.flavor_id)
        self.assertEqual(len(my_flavor.providers), len(self.providers))

    def test_create_no_providers(self):
        self.flavor_id = uuid.uuid1()

        my_flavor = flavor.Flavor(self.flavor_id)

        # test all properties
        self.assertEqual(my_flavor.flavor_id, self.flavor_id)
        self.assertEqual(len(my_flavor.providers), 0)

    def test_provider(self):
        provider_id = uuid.uuid1()
        provider_url = uuid.uuid1()

        new_provider = flavor.Provider(provider_id, provider_url)

        self.assertEqual(new_provider.provider_id, provider_id)
        self.assertEqual(new_provider.provider_url, provider_url)
