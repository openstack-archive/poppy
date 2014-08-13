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

from poppy.transport.validators import schema_base


class ServiceSchema(schema_base.SchemaBase):

    """JSON Schmema validation for /service."""

    schema = {
        'service': {
            'PUT': {
                'type': 'object',
                'properties': {
                    "domains": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    'pattern': "^(([a-zA-Z]{1})|"
                                    "([a-zA-Z]{1}[a-zA-Z]{1})|"
                                    "([a-zA-Z]{1}[0-9]{1})"
                                    "|([0-9]{1}[a-zA-Z]{1})|"
                                    "([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}"
                                    "[a-zA-Z0-9]))\."
                                    "([a-zA-Z]{2,6}|"
                                    "[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$"
                                }}},
                        'required': True,
                        "minItems": 1},
                    "origins": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "origin": {
                                    "type": "string",
                                    "required": True},
                                "port": {
                                    "type": "integer",
                                    "enum": [
                                        80,
                                        443]},
                                "ssl": {
                                    "type": "boolean"}},
                        },
                        'required': True,
                        "minItems": 1},
                    "caching": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "required": True},
                                "ttl": {
                                    "type": "integer",
                                    "required": True},
                                "rules": {
                                    "type": "array",
                                    'items': {
                                        'type': "object",
                                        "properties": {
                                            'name': {
                                                'type': 'string'},
                                            'request_url': {
                                                'type': 'string'}}},
                                }},
                        },
                    },
                }},
            'PATCH': {
                'type': 'object',
                'properties': {
                    "domains": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    'pattern': "^(([a-zA-Z]{1})|"
                                    "([a-zA-Z]{1}[a-zA-Z]{1})|"
                                    "([a-zA-Z]{1}[0-9]{1})"
                                    "|([0-9]{1}[a-zA-Z]{1})|"
                                    "([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}"
                                    "[a-zA-Z0-9]))\."
                                    "([a-zA-Z]{2,6}|"
                                    "[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$"
                                }}},
                    },
                    "origins": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "origin": {
                                    "type": "string",
                                    "required": True},
                                "port": {
                                    "type": "integer",
                                    "enum": [
                                        80,
                                        443]},
                                "ssl": {
                                    "type": "boolean"}},
                        },
                    },
                    "caching": {
                        'type': 'array',
                        'items': {
                            'type': "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "required": True},
                                "ttl": {
                                    "type": "integer",
                                    "required": True},
                                "rules": {
                                    "type": "array",
                                    'items': {
                                        'type': "object",
                                        "properties": {
                                            'name': {
                                                'type': 'string'},
                                            'request_url': {
                                                'type': 'string'}}},
                                }},
                        },
                    },
                }},
        },
    }
