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
from poppy.model.helpers import domain
from poppy.model.helpers import origin


VALID_STATUSES = [u'unknown', u'in_progress', u'deployed', u'failed']


class Service(common.DictSerializableModel):

    def __init__(self, name, domains, origins, caching=[], restrictions=[]):
        self._name = name
        self._domains = domains
        self._origins = origins
        self._caching = caching
        self._restrictions = restrictions
        self._status = u'unknown'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        return [domain.to_dict() for domain in self._domains]

    @domains.setter
    def domains(self, value):
        # explict requirement: value should be a list of dictionary
        # due to weakly typed Python
        self._domains = [domain.Domain.from_dict_init(d) for d in value]

    @property
    def origins(self):
        return [origin.to_dict() for origin in self._origins]

    @origins.setter
    def origins(self, value):
        # explicit requirement: value should be a list of dictionary
        # due to weakly typed Python
        self._origins = [origin.Origin.from_dict_init(d) for d in value]

    @property
    def caching(self):
        return self._caching

    @caching.setter
    def caching(self, value):
        # TODO(tonytan4ever): convert a list of dictionaries into a list of
        # caching rules
        self._caching = value

    @property
    def restrictions(self):
        return self._restrictions

    @restrictions.setter
    def restrictions(self, value):
        # TODO(tonytan4ever): convert a list of dictionaries into a list of
        # restriction
        self._restrictions = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if (value in VALID_STATUSES):
            self._status = value
        else:
            raise ValueError(
                u'Status {0} not in valid options: {1}'.format(
                    value,
                    VALID_STATUSES)
            )

    @classmethod
    def from_dict_init(cls, dict):
        """Construct a model instance from a dictionary.

        This is only meant to be used for converting a
        response model into a model.
        When converting a model into a request model,
        use to_dict.
        """
        o = cls("unamed", [], [])
        o.from_dict(dict)
        return o
