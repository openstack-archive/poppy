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

from poppy.transport.validators import schema_base


class BackgroundJobSchema(schema_base.SchemaBase):

    '''JSON Schmema validation for /admin/provider/akamai/background_jobs'''

    schema = {
        'background_jobs': {
            'POST': {
                'type': [{
                    'additionalProperties': False,
                    'properties': {
                        'job_type': {
                            'type': 'string',
                            'required': True,
                            'enum': ['akamai_check_and_update_cert_status']
                        },
                        'domain_name': {
                            'type': 'string',
                            'required': True
                        },
                        'project_id': {
                            'type': 'string',
                            'required': True
                        },
                        'cert_type': {
                            'type': 'string',
                            'required': True,
                            'enum': ['san']
                        },
                        'flavor_id': {
                            'type': 'string',
                            'required': True
                        }
                    }
                },
                    {
                    'additionalProperties': False,
                    'properties': {
                        'job_type': {
                            'type': 'string',
                            'required': True,
                            'enum': ['akamai_update_papi_property_for_mod_san']
                        },
                        'domain_name': {
                            'type': 'string',
                            'required': True
                        },
                        'san_cert_name': {
                            'type': 'string',
                            'required': True
                        },
                        'update_type': {
                            'type': 'string',
                            'enum': ['hostsnames']
                        },
                        'action': {
                            'type': 'string',
                            'enum': ['add', 'remove']
                        },
                        'property_spec': {
                            'type': 'string',
                            'enum': ['akamai_https_san_config_numbers']
                        },
                        'san_cert_domain_suffix': {
                            'type': 'string'
                        }
                    }
                }]
            }
        }
    }
