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

import json

import pecan
import stoplight

from poppy.transport.validators import pecan_helpers as helpers
from poppy.transport.validators.schemas import service


class MockPecanEndpoint(object):

    testing_schema = service.ServiceSchema.get_schema("service", "POST")

    @stoplight.decorators.validation_function
    def is_valid_json(r):
        """Test for a valid JSON string."""
        if len(r.body) == 0:
            return
        else:
            try:
                json.loads(r.body.decode('utf-8'))
            except Exception as e:
                e
                raise stoplight.exceptions.ValidationFailed(
                    'Invalid JSON string')
            else:
                return

    @pecan.expose(generic=True)
    @helpers.with_schema(pecan.request, schema=testing_schema)
    def index(self):
        return "Hello, World!"

    @index.when(method='PUT')
    @stoplight.decorators.validate(
        request=stoplight.rule.Rule(is_valid_json(),
                                    lambda error_info: pecan.abort(400),
                                    helpers.pecan_getter)
    )
    def index_put(self):
        return "Hello, World!"
