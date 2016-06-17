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


class ProviderNotFound(Exception):

    """Raised when domain is not associated with a known Provider"""


class ProviderDetailsIncomplete(Exception):

    """Raised when domain details with a Provider is incomplete"""


class ServiceNotFound(Exception):

    """Raised when service is not found."""


class ServiceStatusNeitherDeployedNorFailed(Exception):

    """Raised when a neither deployed not failed service is updated with."""


class ServiceStatusNotDeployed(Exception):

    """Raised when a non-deployed service is purged."""


class ServiceStatusDisabled(Exception):

    """Raised when a disabled status is updated."""


class InvalidServiceState(Exception):

    """Raised when a operator state is updated with an invalid status."""


class ServicesOverLimit(Exception):

    """Raised when number of services is above a permissible threshold."""


class SharedShardsExhausted(Exception):

    """Raised when all shared ssl shards are occupied for a given domain."""


class ServiceProviderDetailsNotFound(Exception):

    """Raised when provider details for a service is None."""


class CertificateStatusUpdateError(Exception):

    """Raised when errors encountered updating a certificate."""
