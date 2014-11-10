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


class Flavor(object):
    """Flavor Class."""

    def __init__(self,
                 flavor_id, providers=[]):

        self._flavor_id = flavor_id
        self._providers = providers

    @property
    def flavor_id(self):
        """Get flavor id.

        :returns flavor id
        """
        return self._flavor_id

    @property
    def providers(self):
        """Get providers

        :returns providers
        """
        return self._providers


class Provider(object):
    """Provider Class."""

    def __init__(self,
                 provider_id,
                 provider_url):
        self._provider_id = provider_id
        self._provider_url = provider_url

    @property
    def provider_id(self):
        """Get provider id.

        :returns provider id
        """
        return self._provider_id

    @property
    def provider_url(self):
        """Get provider url.

        :returns provider url
        """
        return self._provider_url
