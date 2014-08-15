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


class FlavorResponseModel(dict):

    def __init__(self, flavor):
        self['flavor_id'] = flavor.flavor_id
        self['providers'] = []

        for x in flavor.providers:
            provider = {}
            provider['provider'] = x.provider_id
            provider['links'] = []

            provider_link = {}
            provider_link['href'] = x.provider_url
            provider_link['rel'] = 'provider_url'
            provider['links'].append(provider_link)

            self['providers'].append(provider)

        self['links'] = []
        flavor_link = {}
        flavor_link['href'] = '/v1.0/flavors/{0}'.format(flavor.flavor_id)
        flavor_link['rel'] = 'self'
        self['links'].append(flavor_link)
