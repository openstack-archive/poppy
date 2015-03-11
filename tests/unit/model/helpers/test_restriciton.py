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

from poppy.model.helpers import restriction
from tests.unit import base


@ddt.ddt
class TestRestriction(base.TestCase):

    def test_restriction(self):

        name = 'restriction'
        myrestriction = restriction.Restriction(name, 'whitelist')

        # test all properties
        # name
        self.assertEqual(myrestriction.name, name)
        # change name and verify that its updated
        name = "new_name"
        myrestriction.name = name
        self.assertEqual(myrestriction.name, name)

        # rules test:
        # We need to be able to set the rule now so previous setattr
        # will be gone
        self.assertEqual(myrestriction.rules, [])
