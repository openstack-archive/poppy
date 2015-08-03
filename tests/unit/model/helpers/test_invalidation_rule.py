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

from poppy.model.helpers import invalidationrule
from poppy.model.helpers import rule
from tests.unit import base


@ddt.ddt
class TestInvalidationRule(base.TestCase):

    def test_invalidation_rule(self):

        name = "rule_name"
        rule_type = "myrule"

        invalidation_rule = \
            invalidationrule.InvalidationRule(name=name,
                                              rule_type=rule_type,
                                              rules=[])

        # test all properties
        # name
        self.assertEqual(invalidation_rule.name, name)
        # change name and verify that its updated
        name = "new_name"
        invalidation_rule.name = name
        self.assertEqual(invalidation_rule.name, name)

        # rule_type
        self.assertEqual(invalidation_rule.rule_type, rule_type)
        # change ttl and verify that its updated
        rule_type = "your_rule"
        invalidation_rule.rule_type = rule_type
        self.assertEqual(invalidation_rule.rule_type, rule_type)

        # default rule is empty list []
        self.assertEqual(invalidation_rule.rules, [])

        # default params is None
        self.assertIsNone(invalidation_rule.params)

    def test_invalidation_rule_serialization(self):
        generic_rule = rule.Rule(name='generic_rule')
        invalidation_dict = {
            'name': 'myinvalidation',
            'rule_type': 'myrule_type',
            'params': {

            },
            'rules': [
                generic_rule.to_dict()
            ]
        }

        obj = invalidationrule.InvalidationRule.init_from_dict(
            invalidation_dict)
        serialized_obj = obj.to_dict()
        self.assertEqual(invalidation_dict['name'],
                         serialized_obj['name'])
        self.assertEqual(invalidation_dict['params'],
                         serialized_obj['params'])
        self.assertEqual(invalidation_dict['rule_type'],
                         serialized_obj['rule_type'])
