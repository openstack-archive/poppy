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

"""DNS Provider implementation."""

from oslo_log import log

from poppy.dns import base
from poppy.dns.default import controllers
from poppy.dns.default.helpers import retry_exceptions


LOG = log.getLogger(__name__)


class DNSProvider(base.Driver):
    """Default DNS Provider."""

    def __init__(self, conf):
        super(DNSProvider, self).__init__(conf)

    def is_alive(self):
        """is_alive.

        :return boolean
        """

        return True

    @property
    def dns_name(self):
        """DNS provider name.

        :return 'Default'
        """

        return 'Default'

    @property
    def client(self):
        """Client to this provider.

        :return None
        """

        return None

    @property
    def services_controller(self):
        """Hook for service controller.

        :return service_controller
        """

        return controllers.ServicesController(self)

    @property
    def retry_exceptions(self):
        """Retry on certain exceptions.

        :return list
        """

        return retry_exceptions
