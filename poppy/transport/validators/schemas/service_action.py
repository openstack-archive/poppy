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


class ServiceActionSchema(schema_base.SchemaBase):

    """JSON Schema validation for /admin/services/action."""

    schema = {
        'service_action': {
            'POST': {
                'type': [{
                    'additionalProperties': False,
                    'properties': {
                        'project_id': {
                            'type': 'string',
                            'required': True
                        },
                        'action': {
                            'enum': ['delete', 'enable', 'disable'],
                            'required': True
                        }
                    }
                },
                    {
                    'additionalProperties': False,
                    'properties': {
                        'action': {
                            'enum': ['delete', 'enable', 'disable'],
                            'required': True
                        },
                        'domain': {
                            'type': 'string',
                            'required': True,
                            'pattern': re.compile('^((?=[a-z0-9-]'
                                                  '{1,63}\.)[a-z0-9]+'
                                                  '(-[a-z0-9]+)*\.)+'
                                                  '[a-z]{2,63}$')
                        }

                    }
                }]
            }
        }
    }
