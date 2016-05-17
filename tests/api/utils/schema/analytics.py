# Copyright (c) 2016 Rackspace, Inc.
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

get_request_count = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'requestCount':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}

get_bandwidthOut = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'bandwidthOut':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}

get_httpResponseCode_2XX = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'httpResponseCode_2XX':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}

get_httpResponseCode_3XX = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'httpResponseCode_3XX':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}

get_httpResponseCode_4XX = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'httpResponseCode_4XX':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}

get_httpResponseCode_5XX = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string', 'format': 'uri'},
        'httpResponseCode_5XX':
            {'type': 'object',
             'properties': {
                 'India': {'type': 'array', 'items': {'type': 'array'}},
                 'EMEA': {'type': 'array', 'items': {'type': 'array'}},
                 'APAC': {'type': 'array', 'items': {'type': 'array'}},
                 'North America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'South America': {
                     'type': 'array', 'items': {'type': 'array'}},
                 'Japan': {'type': 'array', 'items': {'type': 'array'}},
             }},
        'flavor': {'type': 'string', 'enum': ['cdn']},
        'provider': {'type': 'string', 'enum': ['akamai']},
    }
}
