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
                            'type': [{
                                'type': 'object',
                                'properties': {
                                    'domain': {
                                        'type': 'string',
                                        'required': True,
                                        'minLength': 3,
                                        'maxLength': 253,
                                        'pattern': re.compile(
                                            '^(([^:/?#]+):)?'
                                            '(//([^/?#]*))?'
                                            '([^?#]*)(\?([^#]*))?'
                                            '(#(.*))?$',
                                            re.UNICODE
                                        )
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
                                        'maxLength': 253,
                                        'pattern': re.compile(
                                            '^(([^:/?#]+):)?'
                                            '(//([^/?#]*))?'
                                            '([^?#]*)(\?([^#]*))?'
                                            '(#(.*))?$',
                                            re.UNICODE
                                        )
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
                                        'maxLength': 253,
                                        'pattern': re.compile(
                                            '^[^\.]+$',
                                            re.UNICODE
                                        )
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
                                        'maxLength': 253,
                                        'pattern': re.compile(
                                            '^(([^:/?#]+):)?'
                                            '(//([^/?#]*))?'
                                            '([^?#]*)(\?([^#]*))?'
                                            '(#(.*))?$',
                                            re.UNICODE
                                        )
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
                                                'san']
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
                                                'custom']
                                    },
                                    'domain_info': {
                                        'required': True,
                                        'type': 'object',
                                        'properties': {
                                            'registra-country': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'registra-state': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'registra-city': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'registra-orgainzation': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'registra-industry': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-name': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-address': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-city': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-region': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-postal-code': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-country': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'organization-phone': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'admin-contact-first-name': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'admin-contact-last-name': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'admin-contact-phone': {
                                                'required': True,
                                                'type': 'string'
                                            },
                                            'admin-contact-email': {
                                                'required': True,
                                                'type': 'string'
                                            }
                                        }
                                    }
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
                                }
                            }
                        }],
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
                                    "minimum": 0},
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
                                    "minimum": 0},
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
                                'rules': {
                                    'type': 'array',
                                    'required': True,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'required': True,
                                                'minLength': 1,
                                                'maxLength': 256},
                                            'referrer': {
                                                'type': 'string',
                                                'minLength': 3,
                                                'maxLength': 1024}
                                        }},
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
