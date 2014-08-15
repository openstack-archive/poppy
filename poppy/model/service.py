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


VALID_STATUSES = [u'unknown', u'in_progress', u'deployed', u'failed']


class Service(object):

    def __init__(self,
                 name,
                 flavorRef,
                 domains,
                 origins,
                 caching=[],
                 restrictions=[]):
        self._name = name
        self._domains = domains
        self._origins = origins
        self._caching = caching
        self._restrictions = restrictions
        self._flavorRef = flavorRef
        self._links = []
        self._status = 'unknown'

    @property
    def name(self):
        return self._name

    @property
    def domains(self):
        return self._domains

    @property
    def origins(self):
        return self._origins

    @property
    def caching(self):
        return self._caching

    @property
    def restrictions(self):
        return self._restrictions

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
    def flavorRef(self):
        return self._flavorRef

    @property
    def links(self):
        return self._links
