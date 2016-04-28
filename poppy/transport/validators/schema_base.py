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

from poppy.common._i18n import _
from poppy.common import errors


class SchemaBase(object):

    schema = {}

    @classmethod
    def get_schema(cls, resource_name, operation):
        """Returns the schema for an operation

        :param resource_name: Operation for which resource need
        to be validated.
        :type operation: `six.text_type`

        :param operation: Operation for which params need
        to be validated.
        :type operation: `six.text_type`

        :returns: Operation's schema
        :rtype: dict

        :raises: `errors.InvalidResource` if the resource
        does not exist and `errors.InvalidOperation` if the operation
        does not exist
        """
        try:
            resource_schemas = cls.schema[resource_name]
        except KeyError:
            # TODO(tonytan4ever): gettext support
            msg = _('{0} is not a valid resource name').format(resource_name)
            raise errors.InvalidResourceName(msg)

        try:
            return resource_schemas[operation]
        except KeyError:
            # TODO(tonytan4ever): gettext support
            msg = _('{0} is not a valid operation for resource: {1}').format(
                operation,
                resource_name)
            raise errors.InvalidOperation(msg)
