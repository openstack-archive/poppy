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

domain = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string',
                   'pattern': '^([a-zA-Z0-9-.]+(.com))$'}},
        'required': ['domain']
}

origin = {
    'type': 'object',
    'properties': {
        'origin': {'type': 'string',
                   'pattern': '^([a-zA-Z0-9-.]{5,1000})$'},
        'port': {'type': 'number',
                 'minumum': 0,
                 'maximum': 100000},
        'ssl': {'type': 'boolean'},
        'rules': {'type': 'array'}},
    'required': ['origin', 'port', 'ssl'],
    'additionalProperties': False,
}

cache = {'type': 'object',
         'properties': {
             'name': {'type': 'string', 'pattern': '^[a-zA-Z0-9_-]{1,64}$'},
             'ttl': {'type': 'number', 'minimum': 1, 'maximum': 3600},
             'rules': {'type': 'array'}},
         'required': ['name', 'ttl'],
         'additionalProperties': False}

links = {'type': 'object',
         'properties': {
             'href': {'type': 'string',
                      'pattern': '^/v1.0/services/[a-zA-Z0-9_-]{1,64}$'},
             'rel': {'type': 'string'}}
         }

restrictions = {'type': 'array'}

# Response Schema Definition for Create Service API
create_service = {
    'type': 'object',
    'properties': {
        'domains': {'type': 'array',
                    'items': domain,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'origins': {'type': 'array',
                    'items': origin,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'caching': {'type': 'array',
                    'items': cache,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'links': {'type': 'array',
                  'items': links,
                  'minItems': 1,
                  'maxItems': 1},
        'restrictions': restrictions,
    },
    'required': ['domains', 'origins', 'caching', 'links', 'restrictions'],
    'additionalProperties': False}
