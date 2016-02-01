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

retry_item = {
    'type': 'object',
    'properties': {
        'project_id': {'type': 'string'},
        'domain_name': {'type': 'string'},
        'flavor_id': {'type': 'string'},
        'validate_service': {'type': 'boolean'}
    },
    'required': ['project_id', 'domain_name', 'flavor_id'],
    'additionalProperties': False
}

get_retry_list = {'type': 'array', 'items': retry_item}

put_retry_list = {
    'type': 'object',
    'properties': {
        'deleted': {'type': 'array', 'items': retry_item},
        'queue': {'type': 'array', 'items': retry_item}
    },
    'required': ['deleted', 'queue'],
    'additionalProperties': False
}
