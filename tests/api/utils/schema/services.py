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
        'domain': {'type': 'string', 'format': 'uri'},
        'protocol': {'type': 'string', 'enum': ['http']}},
    'required': ['domain'],
    'additionalProperties': False
}

domain_https = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'protocol': {'type': 'string', 'enum': ['https']},
        'certificate':
            {'type': 'string', 'enum': ['shared', 'san', 'custom']},
        'certificate_status':
            {'type': 'string', 'enum': ['deployed',
                                        'create_in_progress',
                                        'failed']}
    },
    'required': ['domain', 'protocol', 'certificate'],
    'additionalProperties': False
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
        'rules': {'type': 'array'},
        'hostheadertype': {'type': 'string'},
        'hostheadervalue': {'type': ['string', 'null']}},
    'required': ['origin', 'port', 'ssl'],
    'additionalProperties': False
}

cache = {'type': 'object',
         'properties': {
             'name': {'type': 'string'},
             'ttl': {'type': 'number', 'minimum': 0},
             'rules': {'type': 'array'}},
         'required': ['name', 'ttl'],
         'additionalProperties': False}

links = {'type': 'object',
         'properties': {
             'href': {'type': 'string', 'format': 'uri'},
             'rel': {'type': 'string', 'enum': ['self', 'access_url',
                                                'flavor', 'log_delivery']}}
         }

error_message = {'type': 'object',
                 'properties': {
                     'message': {'type': 'string'}},
                 'required': ['message'],
                 'additionalProperties': False}

restrictions = {'type': 'array'}
flavor_id = {'type': 'string', 'pattern': '([a-zA-Z0-9_\-]{1,256})'}
log_delivery = {'type': 'object'}
service_name = {'type': 'string', 'pattern': '([a-zA-Z0-9_\-\.]{1,256})'}
uuid4 = '([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})'  # noqa
service_id = {'type': 'string', 'pattern': uuid4}
project_id = {'type': 'string', 'pattern': '([a-zA-Z0-9_\-\.]{1,256})'}

# Response Schema Definition for Get Service API
get_service = {
    'type': 'object',
    'properties': {
        'id': service_id,
        'project_id': project_id,
        'name': service_name,
        'domains': {'type': 'array',
                    'items': {'anyOf': [domain, domain_https]},
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
        'errors': {'type': 'array'},
        'status': {'type': 'string',
                   'enum': ['create_in_progress', 'disabled',
                            'delete_in_progress', 'deployed', 'failed']},
        'restrictions': restrictions,
        'flavor_id': flavor_id,
        'log_delivery': log_delivery,
        'errors': {'type': 'array',
                   'items': error_message}
    },
    'required': ['domains', 'origins', 'links', 'flavor_id', 'status',
                 'errors'],
    'additionalProperties': False}

list_services_link = {
    'type': 'object',
    'properties': {
        'rel': {'type': 'string', 'enum': ['next']},
        'href': {'type': 'string',
                 'pattern':
                 '(https?)(:/{1,3})([a-z0-9\.\-:]{1,400})'
                 '(/v1\.0/([a-z0-9]{1,400}/)?services'
                 '\?marker=)(' + uuid4 + ')'
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
            'maxItems': 1},
        'services': {
            'type': 'array',
            'items': get_service}},
    'required': ['links', 'services'],
    'additionalProperties': False
}
