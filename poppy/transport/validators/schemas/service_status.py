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


class ServiceStatusSchema(schema_base.SchemaBase):

    """JSON Schema validation for /admin/services/{service_id}/status."""

    schema = {
        'service_status': {
            'POST': {
                'type': [{
                    'additionalProperties': False,
                    'properties': {
                        'status': {
                            'enum': [u'deployed',
                                     u'failed'],
                            'required': True
                        },
                        'project_id': {
                            'type': 'string',
                            'required': True,
                            'pattern': re.compile('^([a-zA-Z0-9_\-\.]'
                                                  '{1,256})$')
                        },
                        'service_id': {
                            'type': 'string',
                            'required': True,
                            'pattern': re.compile('^[0-9a-f]{8}-([0-9a-f]'
                                                  '{4}-){3}[0-9a-f]{12}$')
                        },
                    }
                }]
            }
        }
    }
