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


class Origin(common.DictSerializableModel):
    """Origin."""

    def __init__(self, origin, hostheadertype='domain', hostheadervalue='-',
                 port=80, ssl=False, rules=[]):
        self._origin = origin
        self._port = port
        self._ssl = ssl
        self._rules = rules
        self._hostheadertype = hostheadertype
        self._hostheadervalue = hostheadervalue

    @property
    def origin(self):
        """origin."""
        return self._origin

    @origin.setter
    def origin(self, value):
        """origin setter."""
        self._origin = value.strip()

    @property
    def port(self):
        """port.

        :returns port
        """
        return self._port

    @port.setter
    def port(self, value):
        """port setter."""
        self._port = value

    @property
    def ssl(self):
        """self.

        :returns ssl
        """
        return self._ssl

    @ssl.setter
    def ssl(self, value):
        """ssl setter."""
        self._ssl = value

    @property
    def rules(self):
        """rules.

        :returns rules
        """
        return self._rules

    @rules.setter
    def rules(self, value):
        """rules setter."""
        # TODO(tonytan4ever) this field should by typed too
        self._rules = value

    @property
    def hostheadertype(self):
        """hostheadertype."""
        return self._hostheadertype

    @hostheadertype.setter
    def hostheadertype(self, value):
        """hostheadertype setter."""
        self._hostheadertype = value

    @property
    def hostheadervalue(self):
        """hostheadervalue."""
        return self._hostheadervalue

    @hostheadervalue.setter
    def hostheadervalue(self, value):
        """hostheadervalue setter."""
        self._hostheadervalue = value

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """

        o = cls("unnamed")
        o.origin = dict_obj.get("origin", "unnamed").strip()
        o.port = dict_obj.get("port", 80)
        o.ssl = dict_obj.get("ssl", False)
        o.hostheadertype = dict_obj.get("hostheadertype", "domain")
        o.hostheadervalue = dict_obj.get("hostheadervalue", None)
        if o.hostheadertype == 'origin':
            o.hostheadervalue = o.origin
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
        rules_obj_list = result['rules']
        result['rules'] = [r.to_dict() for r in rules_obj_list]
        return result
