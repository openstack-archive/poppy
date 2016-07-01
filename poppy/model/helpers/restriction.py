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


VALID_RESTRICTION_ACCESSES = [
    u'whitelist',
    u'blacklist']


class Restriction(common.DictSerializableModel):

    """Restriction."""

    def __init__(self, name,
                 access='whitelist', rules=[]):
        self._name = name
        self._access = access
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
    def access(self):
        """name.

        :returns name
        """
        return self._access

    @access.setter
    def access(self, value):
        if (value in VALID_RESTRICTION_ACCESSES):
            self._status = value
        else:
            raise ValueError(
                u'Type {0} not in valid options: {1}'.format(
                    value,
                    VALID_RESTRICTION_ACCESSES)
            )

    @property
    def rules(self):
        """rules.

        :returns rules
        """
        return self._rules

    @rules.setter
    def rules(self, value):
        self._rules = value

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """

        access = dict_obj.get("access", 'whitelist')
        o = cls("unnamed", access)
        o.name = dict_obj.get("name", "unnamed").strip()
        rules_dict_list = dict_obj.get("rules", [])
        for val in rules_dict_list:
            val['name'] = val['name'].strip()
            if 'referrer' in val:
                val['referrer'] = val['referrer'].strip()
            elif 'geography' in val:
                val['geography'] = val['geography'].strip()
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
        rules_obj_list = result['rules']
        result['rules'] = [r.to_dict() for r in rules_obj_list]
        return result
