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


VALID_STATUSES = [u'create_in_progress', u'deployed', u'updating',
                  u'delete_in_progress', u'failed']


class Service(common.DictSerializableModel):
    """Service Class."""

    def __init__(self,
                 name,
                 domains,
                 origins,
                 flavor_ref,
                 caching=[],
                 restrictions=[]):
        self._name = name
        self._domains = domains
        self._origins = origins
        self._flavor_ref = flavor_ref
        self._caching = caching
        self._restrictions = restrictions
        self._status = 'create_in_progress'
        self._provider_details = {}

    @property
    def name(self):
        """Get or set name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        """Get or set domains."""
        return self._domains

    @domains.setter
    def domains(self, value):
        self._domains = value

    @property
    def origins(self):
        """Get or set origins."""
        return self._origins

    @origins.setter
    def origins(self, value):
        self._origins = value

    @property
    def flavor_ref(self):
        """Get or set flavor ref."""
        return self._flavor_ref

    @flavor_ref.setter
    def flavor_ref(self, value):
        self._flavor_ref = value

    @property
    def caching(self):
        """Get or set caching."""
        return self._caching

    @caching.setter
    def caching(self, value):
        self._caching = value

    @property
    def restrictions(self):
        """Get or set restrictions."""
        return self._restrictions

    @restrictions.setter
    def restrictions(self, value):
        # TODO(tonytan4ever): convert a list of dictionaries into a list of
        # restriction
        self._restrictions = value

    @property
    def status(self):
        """Get or set status.

        :returns boolean
        """
        # service status is a derived field
        # service will be in creating during service creation
        # if any of the provider services are still in 'deploy_in_progress'
        # status or 'failed' status, the poppy service is still in
        # 'creating' status.
        # if all provider services are in 'deployed' status. the poppy service
        # will be in 'deployed' status
        # if all provider services are in 'delete_in_progress' status.
        # the poppy service will be in 'delete_in_progress' status
        for provider_name in self.provider_details:
            provider_detail = self.provider_details[provider_name]
            if provider_detail.status == u'failed':
                self._status = u'failed'
                break
            elif provider_detail.status == u'delete_in_progress':
                self._status = u'delete_in_progress'
                break
            elif provider_detail.status == u'updating':
                self._status = u'updating'
            elif provider_detail.status == u'deploy_in_progress':
                self._status = u'create_in_progress'
        else:
            if self._status != u'updating' and self.provider_details != {}:
                self._status = 'deployed'

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
        """Get or set provider details."""
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
