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

from poppy.model import common
from poppy.model.helpers import rule


class CachingRule(common.DictSerializableModel):

    """CachingRule

    :param DictSerializableModel:
    """

    def __init__(self, name, ttl, rules=[]):
        self._name = name
        self._ttl = ttl
        self._rules = rules

    @property
    def name(self):
        """name.

        :returns name
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def ttl(self):
        """ttl.

        :returns ttl
        """
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

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

        o = cls("unnamed", 3600)
        o.caching = dict_obj.get("caching", "unnamed")
        o.name = dict_obj.get("name", "unnamed").strip()
        o.ttl = dict_obj.get("ttl", 3600)
        rules_dict_list = dict_obj.get("rules", [])
        for val in rules_dict_list:
            val['name'] = val['name'].strip()
            val['request_url'] = val['request_url'].strip()
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
        result['ttl'] = self._ttl
        rules_obj_list = result['rules']
        result['rules'] = [r.to_dict() for r in rules_obj_list]
        return result
