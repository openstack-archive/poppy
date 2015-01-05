# -*- coding: utf-8 -*-
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

import re

from poppy.transport.validators import schema_base


class ServiceSchema(schema_base.SchemaBase):

    '''JSON Schmema validation for /service.'''

    schema = {
        'service': {
            'POST': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'required': True,
                        'minLength': 3,
                        'maxLength': 256
                    },
                    'domains': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'domain': {
                                    'type': 'string',
                                    'required': True,
                                    'pattern': re.compile(
                                        '^(([^:/?#]+):)?'
                                        '(//([^/?#]*))?'
                                        '([^?#]*)(\?([^#]*))?'
                                        '(#(.*))?$',
                                        re.UNICODE
                                    )
                                },
                                'protocol': {
                                    'type': 'string',
                                    'enum': [
                                            'http',
                                            'https']
                                }}},
                        'required': True,
                        'minItems': 1},
                    'origins': {
                        'type': 'array',
                        # the first origin does not have to
                        # have rules field, it will be defaulted
                        # to global url matching
                        'items': [{
                            'type': 'object',
                            'properties': {
                                'origin': {
                                    'type': 'string',
                                    'pattern': re.compile(
                                        '^(([^:/?#]+):)?'
                                        '(//([^/?#]*))?'
                                        '([^?#]*)(\?([^#]*))?'
                                        '(#(.*))?$',
                                        re.UNICODE
                                    ),
                                    'required': True},
                                'port': {
                                    'type': 'integer',
                                    'enum': [
                                        80,
                                        443]},
                                'ssl': {
                                    'type': 'boolean'},
                                'rules': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True
                                            },
                                            'request_url': {
                                                'type': 'string',
                                                'required': True
                                            }
                                        }
                                    }
                                }
                            }
                        }],
                        'minItems': 1,
                        # the 2nd and successive items must have
                        # 'rules' field which has at least one rule
                        "additionalItems": {
                            'type': 'object',
                            'properties': {
                                'origin': {
                                    'type': 'string',
                                    'pattern': re.compile(
                                        '^(([^:/?#]+):)?'
                                        '(//([^/?#]*))?'
                                        '([^?#]*)(\?([^#]*))?'
                                        '(#(.*))?$',
                                        re.UNICODE
                                    ),
                                    'required': True},
                                'port': {
                                    'type': 'integer',
                                    'enum': [
                                        80,
                                        443]},
                                'ssl': {
                                    'type': 'boolean'},
                                'rules': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True
                                            },
                                            'request_url': {
                                                'type': 'string',
                                                'required': True
                                            }
                                        }
                                    },
                                    'required': True,
                                    'minItems': 1,
                                },
                            }
                        }
                    },
                    'caching': {
                        'type': 'array',
                        'required': False,
                        'items': [{
                            'type': 'object',
                            'required': False,
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'required': True},
                                'ttl': {
                                    'type': 'integer',
                                    'required': True},
                                'rules': {
                                    'type': 'array',
                                    'required': False,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True},
                                            'request_url': {
                                                'type': 'string',
                                                'required': True}}},
                                }},
                        }],
                        "additionalItems": {
                            'type': 'object',
                            'required': False,
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'pattern': re.compile(
                                        '^(?!default$).*',
                                        re.IGNORECASE
                                    ),
                                    'required': True},
                                'ttl': {
                                    'type': 'integer',
                                    'required': True},
                                'rules': {
                                    'type': 'array',
                                    'required': True,
                                    'minItems': 1,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string'},
                                            'request_url': {
                                                'type': 'string'}}},
                                }},
                        },
                        "uniqueItems": True,
                    },
                    'restrictions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'required': True},
                                'rules': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string'},
                                            'referrer': {
                                                'type': 'string'},
                                            'request_url': {
                                                'type': 'string'},
                                            'http_host': {
                                                'type': 'string'},
                                            'client_ip': {
                                                'type': 'string'},
                                            'http_method': {
                                                'type': 'string',
                                                'enum': [
                                                    'GET',
                                                    'PUT',
                                                    'POST',
                                                    'PATCH']}}},
                                }},
                        },
                    },
                    'flavor_id': {
                        'type': 'string',
                        'required': True,
                    }
                }},
            'PATCH': {
                'type': 'array',
                'properties': {
                    'op': {
                        'type': 'string',
                        'enum': [
                            'add',
                            'remove',
                            'replace'
                        ]
                    },
                    'path': {
                        'type': 'string',
                        'enum': [
                            'service_name',
                            'flavor_id',
                            'origins',
                            'domains',
                            'caching_rule',
                            'restrictions'
                        ]
                    },
                    'value': {
                        'oneOf': [
                            'string',
                            'integer'
                        ]
                    }
                }
            },
        },
    }
