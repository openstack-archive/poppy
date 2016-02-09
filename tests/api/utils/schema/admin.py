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

# Response Schema Definition for Get Service ids and Project id by status

from tests.api.utils.schema.services import project_id
from tests.api.utils.schema.services import service_id

get_service_project_status = {
    'items': [
        {
            'type': 'object',
            'properties': {
                'service_id': service_id,
                'project_id': project_id,
            },
            'required': ['service_id', 'project_id'],
            'additionalProperties': False
        }
    ]
}
