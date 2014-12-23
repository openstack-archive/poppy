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

try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

from poppy.transport.pecan.models.response import link


class Model(collections.OrderedDict):

    def __init__(self, flavor, controller):
        super(Model, self).__init__()

        self['id'] = flavor.flavor_id
        self['providers'] = []

        for x in flavor.providers:
            provider = collections.OrderedDict()
            provider['provider'] = x.provider_id
            provider['links'] = []
            provider['links'].append(
                link.Model(x.provider_url, 'provider_url'))

            self['providers'].append(provider)

        self['links'] = []
        self['links'].append(
            link.Model(
                u'{0}/flavors/{1}'.format(controller.base_url,
                                          flavor.flavor_id),
                'self'))
