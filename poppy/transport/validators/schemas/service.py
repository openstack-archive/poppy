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
    '''JSON Schema validation for /service.'''

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
                            'type': [{
                                'type': 'object',
                                'properties': {
                                    'domain': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253
                                    }
                                },
                                "additionalProperties": False
                            }, {
                                'type': 'object',
                                'properties': {
                                    'domain': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253
                                    },
                                    'protocol': {
                                        'required': True,
                                        'type': 'string',
                                        'enum': [
                                            'http']
                                    },
                                    # When protocol is http
                                    # certificate must be null
                                    'certificate': {
                                        'type': ['null']
                                    },
                                },
                                "additionalProperties": False
                            }, {
                                'type': 'object',
                                'properties': {
                                    'domain': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253
                                    },
                                    'protocol': {
                                        'required': True,
                                        'type': 'string',
                                        'enum': [
                                            'https']
                                    },
                                    'certificate': {
                                        'required': True,
                                        'type': 'string',
                                        'enum': [
                                            'shared']
                                    },
                                },
                                "additionalProperties": False
                            }, {
                                'type': 'object',
                                'properties': {
                                    'domain': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253
                                    },
                                    'protocol': {
                                        'required': True,
                                        'type': 'string',
                                        'enum': [
                                            'https']
                                    },
                                    'certificate': {
                                        'required': True,
                                        'type': 'string',
                                        'enum': [
                                            'san',
                                            'custom']
                                    },
                                },
                                "additionalProperties": False
                            }]
                        },
                        'required': True,
                        'minItems': 1,
                        'maxItems': 10},
                    'origins': {
                        'type': 'array',
                        # the first origin does not have to
                        # have rules field, it will be defaulted
                        # to global url matching
                        'items': {
                            'type': [{
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
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253},
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
                                                    'required': True,
                                                    'minLength': 1,
                                                    'maxLength': 256
                                                },
                                                'request_url': {
                                                    'type': 'string',
                                                    'required': True,
                                                    'minLength': 1,
                                                    'maxLength': 1024
                                                }
                                            }
                                        }
                                    },
                                    'hostheadertype': {
                                        'type': 'string',
                                        'enum': ['domain', 'origin'],
                                        'required': False,
                                    },
                                }
                            }, {
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
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253},
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
                                                    'required': True,
                                                    'minLength': 1,
                                                    'maxLength': 256
                                                },
                                                'request_url': {
                                                    'type': 'string',
                                                    'required': True,
                                                    'minLength': 1,
                                                    'maxLength': 1024
                                                }
                                            }
                                        }
                                    },
                                    'hostheadertype': {
                                        'type': 'string',
                                        'enum': ['custom'],
                                        'required': False,
                                    },
                                    'hostheadervalue': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253
                                    }
                                }
                            }
                            ]},
                        'required': True,
                        'minItems': 1,
                        'maxItems': 10,
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
                                    'required': True,
                                    'minLength': 3,
                                    'maxLength': 253},
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
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 256,
                                            },
                                            'request_url': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 1024,
                                            }
                                        }
                                    },
                                    'required': True,
                                    'minItems': 1,
                                },
                                'hostheadertype': {
                                    'type': 'string',
                                    'enum': ['domain', 'origin'],
                                    'required': False,
                                }
                            },
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
                                    'required': True,
                                    'minLength': 3,
                                    'maxLength': 253},
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
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 256,
                                            },
                                            'request_url': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 1024,
                                            }
                                        }
                                    },
                                    'required': True,
                                    'minItems': 1,
                                },
                                'hostheadertype': {
                                    'type': 'string',
                                    'enum': ['custom'],
                                    'required': False,
                                },
                                'hostheadervalue': {
                                    'type': 'string',
                                    'required': True,
                                    'minLength': 3,
                                    'maxLength': 253
                                }
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
                                    'required': True,
                                    'minLength': 1,
                                    'maxLength': 256},
                                'ttl': {
                                    'type': 'integer',
                                    'required': True,
                                    "minimum": 0,
                                    "maximum": 31536000},
                                'rules': {
                                    'type': 'array',
                                    'required': False,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 256},
                                            'request_url': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 1024}}},
                                }},
                        }],
                        "additionalItems": {
                            'type': 'object',
                            'required': False,
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'required': True,
                                    'minLength': 1,
                                    'maxLength': 256},
                                'ttl': {
                                    'type': 'integer',
                                    'required': True,
                                    "minimum": 0,
                                    "maximum": 31536000},
                                'rules': {
                                    'type': 'array',
                                    'required': True,
                                    'minItems': 1,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 256},
                                            'request_url': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 1024}}},
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
                                    'required': True,
                                    'minLength': 1,
                                    'maxLength': 256},
                                'access': {
                                    'type': 'string',
                                    'enum': [
                                        "whitelist",
                                        "blacklist"]},
                                'rules': {
                                    'type': 'array',
                                    'required': True,
                                    'items': {
                                        'type': [
                                            {
                                                'type': 'object',
                                                "properties": {
                                                    "name": {
                                                        "type": "string",
                                                        'minLength': 1,
                                                        'maxLength': 256,
                                                        "required": True,
                                                    },
                                                    "referrer": {
                                                        "type": "string",
                                                        'required': True,
                                                        'minLength': 3,
                                                        'maxLength': 1024
                                                    },
                                                    'request_url': {
                                                        'type': 'string',
                                                        'minLength': 1,
                                                        'maxLength': 1024
                                                    }
                                                },
                                                "additionalProperties": False,
                                            }, {
                                                'type': 'object',
                                                "properties": {
                                                    "name": {
                                                        "type": "string",
                                                    },
                                                    "geography": {
                                                        "type": "string",
                                                        'required': True,
                                                    },
                                                    'request_url': {
                                                        'type': 'string',
                                                        'minLength': 2,
                                                        'maxLength': 100
                                                    }
                                                },
                                                "additionalProperties": False
                                            }, {
                                                'type': 'object',
                                                "properties": {
                                                    "name": {
                                                        "type": "string",
                                                    },
                                                    "client_ip": {
                                                        "type": "string",
                                                        'pattern': re.compile(
                                                            # ipV6 address
                                                            "(^(([0-9a-fA-F]"
                                                            "{1,4}:){7,7}"
                                                            "[0-9a-fA-F]{1,4}"
                                                            "|([0-9a-fA-F]"
                                                            "{1,4}:){1,7}:|"
                                                            "([0-9a-fA-F]"
                                                            "{1,4}:){1,6}:"
                                                            "[0-9a-fA-F]"
                                                            "{1,4}|"
                                                            "([0-9a-fA-F]{1,4}"
                                                            ":){1,5}(:"
                                                            "[0-9a-fA-F]{1,4})"
                                                            "{1,2}|([0-9a-fA-F"
                                                            "]{1,4}:){1,4}(:["
                                                            "0-9a-fA-F]{1,4})"
                                                            "{1,3}|([0-9a-fA-F"
                                                            "]{1,4}:){1,3}(:[0"
                                                            "-9a-fA-F]{1,4}){"
                                                            "1,4}|([0-9a-fA-F]"
                                                            "{1,4}:){1,2}(:[0-"
                                                            "9a-fA-F]{1,4}){1,"
                                                            "5}|[0-9a-fA-F]{1,"
                                                            "4}:((:[0-9a-fA-F]"
                                                            "{1,4}){1,6})|:((:"
                                                            "[0-9a-fA-F]{1,4})"
                                                            "{1,7}|:)|fe80:(:["
                                                            "0-9a-fA-F]{0,4}){"
                                                            "0,4}%[0-9a-zA-Z]"
                                                            "{1,}|::(ffff(:0{1"
                                                            ",4}){0,1}:){0,1}("
                                                            "(25[0-5]|(2[0-4]|"
                                                            "1{0,1}[0-9]){0,1}"
                                                            "[0-9])\.){3,3}(25"
                                                            "[0-5]|(2[0-4]|1{0"
                                                            ",1}[0-9]){0,1}[0-"
                                                            "9])|([0-9a-fA-F]{"
                                                            "1,4}:){1,4}:((25["
                                                            "0-5]|(2[0-4]|1"
                                                            "{0,1}[0-9]){0,1}"
                                                            "[0-9])\.){3,3}("
                                                            "25[0-5]|(2[0-4]|"
                                                            "1{0,1}[0-9]){0,1"
                                                            "}[0-9]))(\/("
                                                            "[1-9]|[1-9][0-9]|"
                                                            "1[0-1][0-9]|12[0"
                                                            "-8]))?$)"
                                                            # IPv4 Address
                                                            "|(^(((25[0-5]|"
                                                            "(2[0-4]|1{0,1}"
                                                            "[0-9]){0,1}[0-9])"
                                                            "\.){3,3}(25[0-5]|"
                                                            "(2[0-4]|1{0,1}"
                                                            "[0-9]){0,1}[0-9])"
                                                            ")(\/([1-9]"
                                                            "|[1-2][0-9]|"
                                                            "3[0-2]))?$)"
                                                        ),
                                                        'required': True,
                                                    },
                                                    'request_url': {
                                                        'type': 'string',
                                                        'minLength': 2,
                                                        'maxLength': 100
                                                    }
                                                },
                                                "additionalProperties": False
                                            }
                                        ]
                                    }
                                }},
                        },
                    },
                    'flavor_id': {
                        'type': 'string',
                        'required': True,
                        'minLength': 1,
                        'maxLength': 256
                    },
                    'log_delivery': {
                        'type': 'object',
                        'required': False,
                        'properties': {
                            'enabled': {
                                'type': 'boolean',
                                'required': True
                            }
                        }
                    }
                }
            },
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
                            'restrictions',
                            'log_delivery'
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
