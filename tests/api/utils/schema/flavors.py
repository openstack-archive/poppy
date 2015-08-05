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

# Definition for components of Get Flavor API Schema
provider_link = {'type': 'object',
                 'properties': {
                     'href': {'type': 'string', 'format': 'uri'},
                     'rel': {'type': 'string', 'enum': ['provider_url']}},
                 'required': ['href', 'rel'],
                 'additionalProperties': False}

provider = {'type': 'object',
            'properties': {'provider': {'type': 'string'},
                           'links': {'type': 'array',
                                     'items': provider_link,
                                     'minItems': 1,
                                     'maxItems': 1}},
            'required': ['provider', 'links'],
            'additionalProperties': False}

link = {'type': 'object',
        'properties': {
            'href': {'type': 'string',
                     'oneOf': [
                         {'pattern': '^(https?)(:/{1,3})([a-z0-9\.\-:]{1,400})'
                          '/v1\.0/flavors/'},
                         {'pattern': '^(https?)(:/{1,3})([a-z0-9\.\-:]{1,400})'
                          '/v1\.0/([a-z0-9]{1,400})/flavors/'}]},
            'rel': {'type': 'string', 'enum': ['self']}},
        'required': ['href', 'rel'],
        'additionalProperties': False}

# Response Schema definition for Get Flavor API

get_flavor = {
    'type':
    'object',
    'properties': {
        'id': {'type': 'string'},
        'providers': {'type': 'array',
                      'items': provider,
                      'minItems': 1
                      },
        'links': {'type': 'array',
                  'items': link,
                  'minItems': 1,
                  'maxItems': 1}
    },
    'required': ['id', 'providers', 'links'],
    'additionalProperties': False
}

# Response Schema definition for List Flavors API
list_flavors = {
    'type': 'object',
    'properties': {
        'flavors': {'type': 'array',
                    'items': get_flavor,
                    'minItems': 1
                    }
    },
    'required': ['flavors'],
    'additionalProperties': False
}
