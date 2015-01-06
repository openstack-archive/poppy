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

AVAILABLE_PROTOCOLS = [
    u'http',
    u'https']

from poppy.model import common


class Domain(common.DictSerializableModel):

    def __init__(self, domain, protocol='http'):
        self._domain = domain

        if (protocol in AVAILABLE_PROTOCOLS):
            self._protocol = protocol
        else:
            raise ValueError(
                u'Protocol: {0} not in currently available'
                ' protocols: {1}'.format(
                    protocol,
                    AVAILABLE_PROTOCOLS)
            )

    @property
    def domain(self):
        """domain.

        :returns domain
        """
        return self._domain

    @domain.setter
    def domain(self, value):
        """domain setter."""
        self._domain = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if (value in AVAILABLE_PROTOCOLS):
            self._protocol = value
        else:
            raise ValueError(
                u'Protocol: {0} not in currently available'
                ' protocols: {1}'.format(
                    value,
                    AVAILABLE_PROTOCOLS)
            )

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """
        o = cls("")
        o.domain = dict_obj.get("domain", "")
        o.protocol = dict_obj.get("protocol", "http")
        return o
