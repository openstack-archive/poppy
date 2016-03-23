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

from poppy.transport.validators import schema_base


class FlavorSchema(schema_base.SchemaBase):

    """JSON Schema validation for /flavor."""

    schema = {
        "flavor": {
            "POST": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 64,
                        "required": True
                    },
                    "providers": {
                        "type": "array",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "provider": {
                                    "type": "string",
                                    "required": True
                                },
                                "links": {
                                    "type": "array",
                                    "required": True,
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "href": {
                                                "type": "string",
                                                "minLength": 2,
                                                "required": True
                                            },
                                            "rel": {
                                                "type": "string",
                                                "enum": ["provider_url"],
                                                "required": True
                                            }
                                        }
                                    },
                                    "minItems": 1
                                }
                            }
                        },
                        "minItems": 1
                    }
                }
            }
        }
    }
