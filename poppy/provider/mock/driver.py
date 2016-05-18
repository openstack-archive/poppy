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

"""CDN Provider implementation."""

from oslo_log import log

from poppy.provider import base
from poppy.provider.mock import controllers

LOG = log.getLogger(__name__)


class CDNProvider(base.Driver):
    """Mock CDNProvider."""

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)
        self.regions = []

    def is_alive(self):
        """is_alive.

        :return True
        """
        return True

    @property
    def provider_name(self):
        """provider name.

        :return 'Mock'
        """
        return "Mock"

    @property
    def service_controller(self):
        """Hook for service controller.

        :return service controller
        """
        return controllers.ServiceController(self)

    @property
    def certificate_controller(self):
        """Hook for certificate controller.

        :return certificate controller
        """
        return controllers.CertificateController(self)
