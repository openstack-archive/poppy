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


class Restriction(common.DictSerializableModel):

    """Restriction."""

    def __init__(self, name, rules=[]):
        self._name = name
        self._rules = rules

    @property
    def name(self):
        """name.

        :returns name
        """
        return self._name

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
        o = cls(
            dict_obj.get("name", "unnamed"),
            dict_obj.get("rules", [])
        )
        return o

    def to_dict(self):
        result = common.DictSerializableModel.to_dict(self)
        # need to deserialize the nested rules object
        rules_obj_list = result['rules']
        result['rules'] = [r.to_dict() for r in rules_obj_list]
        return result
