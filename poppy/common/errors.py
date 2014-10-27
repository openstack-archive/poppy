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


class InvalidResourceName(Exception):

    """Raised when attempted a non existent resource."""


class InvalidOperation(Exception):

    """Raised when attempted a non existent operation."""


class BadProviderDetail(Exception):

    """Raised when attempted a non existent operation."""


class ServiceStatusNotDeployed(Exception):

    """Raised when attempted to update service who status is not deployed."""
