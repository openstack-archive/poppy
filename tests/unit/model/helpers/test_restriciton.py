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
        myrestriction = restriction.Restriction(name)

        # test all properties
        # name
        self.assertEqual(myrestriction.name, name)
        self.assertRaises(AttributeError, setattr, myrestriction, 'name', name)

        # rules
        self.assertEqual(myrestriction.rules, [])
        self.assertRaises(AttributeError, setattr, myrestriction, 'rules', [])
