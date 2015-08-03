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

from poppy.model import common
from poppy.model.helpers import rule


class InvalidationRule(common.DictSerializableModel):

    """InvalidationRule

    :param DictSerializableModel:
    """

    def __init__(self, name, rule_type, params=None, rules=[]):
        self._name = name
        self._rule_type = rule_type
        self._params = params
        self._rules = rules

    @property
    def name(self):
        """name.

        :returns name
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def rule_type(self):
        """rule_type.

        :returns rule_type
        """
        return self._rule_type

    @rule_type.setter
    def rule_type(self, value):
        self._rule_type = value

    @property
    def params(self):
        """associated params for invalidation rule

        :returns params
        """
        return self._rule_type

    @params.setter
    def params(self, value):
        self._parms = value

    @property
    def rules(self):
        """rules.

        :returns rules
        """
        return self._rules

    @rules.setter
    def rules(self, value):
        """rules.

        :returns rules
        """
        self._rules = value

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """

        o = cls("unnamed", "unnamed", {})
        o.name = dict_obj.get("name", "unnamed")
        o.rule_type = dict_obj.get("rule_type", "unnamed")
        o.params = dict_obj.get("params", {})
        rules_dict_list = dict_obj.get("rules", [])
        o.rules = []
        for rule_dict in rules_dict_list:
            new_rule = rule.Rule(rule_dict['name'])
            del rule_dict['name']
            new_rule.from_dict(rule_dict)
            o.rules.append(new_rule)
        return o

    def to_dict(self):
        result = common.DictSerializableModel.to_dict(self)
        # need to deserialize the nested rules object
        result['name'] = self._name
        result['rule_type'] = self._rule_type
        result['params'] = self._params
        rules_obj_list = result['rules']
        result['rules'] = [r.to_dict() for r in rules_obj_list]
        return result
