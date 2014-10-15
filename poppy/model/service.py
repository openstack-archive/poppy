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


VALID_STATUSES = [u'creating', u'deployed', u'updating', u'delete_in_progress']


class Service(common.DictSerializableModel):

    def __init__(self,
                 name,
                 domains,
                 origins,
                 flavorRef,
                 caching=[],
                 restrictions=[]):
        self._name = name
        self._domains = domains
        self._origins = origins
        self._flavorRef = flavorRef
        self._caching = caching
        self._restrictions = restrictions
        self._status = u'creating'
        self._provider_details = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        return self._domains

    @domains.setter
    def domains(self, value):
        self._domains = value

    @property
    def origins(self):
        return self._origins

    @origins.setter
    def origins(self, value):
        self._origins = value

    @property
    def flavorRef(self):
        return self._flavorRef

    @flavorRef.setter
    def flavorRef(self, value):
        self._flavorRef = value

    @property
    def caching(self):
        return self._caching

    @caching.setter
    def caching(self, value):
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

    @property
    def provider_details(self):
        return self._provider_details

    @provider_details.setter
    def provider_details(self, value):
        self._provider_details = value

    @classmethod
    def init_from_dict(cls, input_dict):
        """Construct a model instance from a dictionary.

        This is only meant to be used for converting a
        response model into a model.
        When converting a model into a request model,
        use to_dict.
        """
        o = cls('unnamed', [], [], 'unnamed')
        o.from_dict(input_dict)
        return o
