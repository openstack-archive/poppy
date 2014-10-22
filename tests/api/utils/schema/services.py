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

# Definition for components of Create Service API Schema
domain = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'}},
    'required': ['domain']
}

origin = {
    'type': 'object',
    'properties': {
        'origin': {'type': 'string',
                   'format': 'uri'},
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
             'href': {'type': 'string', 'format': 'uri'},
             'rel': {'type': 'string', 'enum': ['self', 'access_url']}}
         }

restrictions = {'type': 'array'}
flavor_id = {'type': 'string', 'pattern': '([a-zA-Z0-9_\-]{1,256})'}
service_name = {'type': 'string', 'pattern': '([a-zA-Z0-9_\-\.]{1,256})'}

# Response Schema Definition for Get Service API
get_service = {
    'type': 'object',
    'properties': {
        'name': service_name,
        'domains': {'type': 'array',
                    'items': domain,
                    'minItems': 1
                    },
        'origins': {'type': 'array',
                    'items': origin,
                    'minItems': 1
                    },
        'caching': {'type': 'array',
                    'items': cache,
                    },
        'links': {'type': 'array',
                  'items': links,
                  'minItems': 1},
        'status': {'type': 'string',
                   # TODO(malini): Uncomment below after status is implemented
                   # 'enum': ['in_progress', 'deployed', 'unknown', 'failed']
                   },
        'restrictions': restrictions,
        'flavorRef': flavor_id
    },
    'required': ['domains', 'origins', 'links', 'flavorRef', 'status'],
    'additionalProperties': False}

list_services_link = {
    'type': 'object',
    'properties': {
        'rel': {'type': 'string', 'enum': ['next']},
        'href': {'type': 'string',
                 'pattern':
                 '(https?)(:/{1,3})([a-z0-9\.\-:]{1,400})'
                 '(/v1\.0/services\?marker=)([a-zA-Z0-9_\-\.]{1,256})'
                 '(&limit=)([1-9]|1[0-9])'}},
        'required': ['rel', 'href'],
        'additionalProperties': False}

# Response Schema Definition for List Services API
list_services = {
    'type': 'object',
    'properties': {
        'links': {
            'type': 'array',
            'items': list_services_link,
            'minItems': 1,
            'maxItems': 1},
        'services': {
            'type': 'array',
            'items': get_service}},
    'required': ['links', 'services'],
    'additionalProperties': False
}
