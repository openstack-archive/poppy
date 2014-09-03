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


class ProviderDetail(object):

    '''ProviderDetail object for each provider.'''

    def __init__(self, id=None, access_url=None, status=u"unknown", name=None):
        self._id = id
        self._access_url = access_url
        self._status = status
        self._name = name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def access_url(self):
        return self._access_url

    @access_url.setter
    def access_url(self, value):
        self._access_url = value

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
