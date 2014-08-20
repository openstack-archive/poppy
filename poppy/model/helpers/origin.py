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


class Origin(common.DictSerializableModel):

    def __init__(self, origin, port=80, ssl=False):
        self._origin = origin
        self._port = port
        self._ssl = ssl
        self._rules = []

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def ssl(self):
        return self._ssl

    @ssl.setter
    def ssl(self, value):
        self._ssl = value

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, value):
        # TODO(tonytan4ever) this field should by typed too
        self._rules = value

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor
        """
        o = cls("unnamed")
        o.origin = dict_obj.get("origin", "unnamed")
        o.port = dict_obj.get("port", 80)
        o.ssl = dict_obj.get("ssl", False)
        return o
