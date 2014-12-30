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

import jsonschema
import pecan


def deserialize_json(schema, model=None):
    """Deserializes json object."""
    def _wrapper(func):
        def wrapper(*args, **kwargs):
            v = jsonschema.Draft4Validator(schema)
            errors = {}
            try:
                data = pecan.request.json
            except ValueError:
                pecan.response.status = 400
                pecan.response.content_type = "application/json"
                pecan.response.json = {
                    "message": (
                        "Unable to parse valid JSON from the request body "
                        "when the Content-Type header indicated "
                        "application/json"
                    )
                }
                return pecan.response

            for e in v.iter_errors(data):
                if len(e.path) > 0:
                    key = e.path.pop()
                    if key not in errors:
                        errors[key] = []
                    errors[key].append(e.message)
                else:
                    if "additional_errors" not in errors:
                        errors["additional_errors"] = []
                    errors["additional_errors"].append(e.message)

            if errors:
                pecan.response.status = 400
                pecan.response.content_type = "application/json"
                pecan.response.json = {
                    "message": (
                        "The provided JSON did not adhere to the schema"
                    ),
                    "errors": errors,
                    "schema": schema
                }
                return pecan.response

            kwargs["request_json"] = data
            if model:
                kwargs["request_model"] = model(data)

            return func(*args, **kwargs)
        return wrapper
    return _wrapper
