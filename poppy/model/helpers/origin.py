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
    """Origin."""

    def __init__(self, origin, port=80, ssl=False):
        self._origin = origin
        self._port = port
        self._ssl = ssl
        self._rules = []

    @property
    def origin(self):
        """origin."""
        return self._origin

    @origin.setter
    def origin(self, value):
        """origin setter."""
        self._origin = value

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

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """

        o = cls("unnamed")
        o.origin = dict_obj.get("origin", "unnamed")
        o.port = dict_obj.get("port", 80)
        o.ssl = dict_obj.get("ssl", False)
        return o
