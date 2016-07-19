# Copyright (c) 2015 Rackspace, Inc.
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


class SSLCertificateSchema(schema_base.SchemaBase):

    '''JSON Schema validation for /ssl_certificate.'''

    schema = {
        'ssl_certificate': {
            'POST': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'flavor_id': {
                        'type': 'string',
                        'required': True,
                        'minLength': 1,
                        'maxLength': 256
                    },
                    'cert_type': {
                        'type': 'string',
                        'required': True,
                        'enum': ['san'],
                    },
                    'domain_name': {
                        'type': 'string',
                        'required': True,
                        'minLength': 3,
                        'maxLength': 253
                    },
                    'project_id': {
                        'type': 'string',
                        'required': True,
                    }
                }
            }
        },

        'retry_list': {
            'PUT': {
                'type': 'array',
                "uniqueItems": True,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'flavor_id': {
                            'type': 'string',
                            'required': True,
                            'minLength': 1,
                            'maxLength': 256
                        },
                        'domain_name': {
                            'type': 'string',
                            'required': True,
                            'minLength': 3,
                            'maxLength': 253
                        },
                        'project_id': {
                            'type': 'string',
                            'minLength': 1,
                            'pattern': re.compile('^([a-zA-Z0-9_\-\.]'
                                                  '{1,256})$'),
                            'required': True,
                        },
                        'validate_service': {
                            'type': 'boolean'
                        }
                    }
                }
            }
        },

        'config': {
            'POST': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'spsId': {
                        'type': 'integer',
                        # we cannot have 0 or negative spsId
                        'minimum': 1
                    },
                    'enabled': {
                        'type': 'boolean'
                    },
                    'san_cert_hostname_limit': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 200,
                    }
                }
            }
        },

        'san_mapping_list': {
            'PUT': {
                'type': 'array',
                "uniqueItems": True,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'domain_name': {
                            'type': 'string',
                            'required': True,
                            'minLength': 3,
                            'maxLength': 253
                        },
                        'cert_details': {
                            'type': 'object',
                            'required': True,
                            'additionalProperties': False,
                            'properties': {
                                'Akamai': {
                                    'type': 'object',
                                    'required': True,
                                    'additionalProperties': False,
                                    'properties': {
                                        'extra_info': {
                                            'type': 'object',
                                            'required': True,
                                            'properties': {
                                                'san cert': {
                                                    'type': 'string',
                                                    'required': True,
                                                    'minLength': 3,
                                                    'maxLength': 253
                                                },
                                                'akamai_spsId': {
                                                    'type': 'integer',
                                                    'required': True
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        'flavor_id': {
                            'type': 'string',
                            'required': True,
                            'minLength': 1,
                            'maxLength': 256
                        },
                        'project_id': {
                            'type': 'string',
                            'required': True,
                        },
                        'cert_type': {
                            'type': 'string',
                            'required': True,
                            'enum': ['san'],
                        }
                    }
                }
            }
        },

        'admin_cert_status': {
            'PATCH': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 1,
                'additionalItems': False,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'op': {
                            'type': 'string',
                            'enum': [
                                'replace',
                            ],
                            'required': True,
                        },
                        'path': {
                            'type': 'string',
                            'enum': ['status'],
                            'required': True,
                        },
                        'value': {
                            'type': 'string',
                            'enum': [
                                'cancelled',
                                'create_in_progress',
                                'deployed',
                                'failed'
                            ],
                            'required': True,
                        }
                    }
                }
            }
        }
    }
