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

from poppy.model import flavor
from poppy.storage import base


CQL_GET_OPERATOR_STATUS = '''
    SELECT operator_status
    FROM services
    WHERE project_id = %(project_id)s AND service_id = %(service_id)s
'''

CQL_UPDATE_OPERATOR_STATUS = '''
    INSERT INTO flavors (flavor_id,
        providers)
    VALUES (%(flavor_id)s,
        %(providers)s)
'''


@six.add_metaclass(abc.ABCMeta)
class OperatorStatusControllerBase(controller.StorageControllerBase):
    """Operator Status Controller Base definition."""

    def __init__(self, driver):
        super(OperatorStatusControllerBase, self).__init__(driver)

    def get(self):
        """Return operator status of the service."""

        raise NotImplementedError

    def set(self, operator_status):
        """Sets operator status of the service."""

        raise NotImplementedError
