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

from poppy.model import flavor


def load_from_json(json_data):

    flavor_id = json_data['id']
    providers = []

    for p in json_data['providers']:
        provider_id = p['provider']
        provider_url = [item['href']
                        for item in p['links']
                        if item['rel'] == 'provider_url'][0]

        provider = flavor.Provider(provider_id, provider_url)
        providers.append(provider)

    new_flavor = flavor.Flavor(flavor_id, providers)

    return new_flavor
