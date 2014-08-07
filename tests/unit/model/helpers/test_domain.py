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


import ddt

from poppy.model.helpers import domain
from tests.unit import base


@ddt.ddt
class TestDomain(base.TestCase):

    def test_domain(self):

        domain_name = 'www.mydomain.com'
        mydomain = domain.Domain(domain_name)

        # test all properties
        # domain
        self.assertEqual(mydomain.domain, domain_name)
        self.assertRaises(
            AttributeError, setattr, mydomain, 'domain', domain_name)
