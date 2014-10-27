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

"""Fastly CDN Provider implementation."""

import fastly
from oslo.config import cfg
import requests

from poppy.openstack.common import log as logging
from poppy.provider import base
from poppy.provider.fastly import controllers

LOG = logging.getLogger(__name__)

FASTLY_OPTIONS = [
    cfg.StrOpt('apikey', help='Fastly API Key'),
]

FASTLY_GROUP = 'drivers:provider:fastly'
FASTLY_ENDPOINT = 'https://api.fastly.com/'


class CDNProvider(base.Driver):
    """Fastly CNDProvider."""

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(FASTLY_OPTIONS,
                                 group=FASTLY_GROUP)
        self.fastly_conf = self._conf[FASTLY_GROUP]

        self.fastly_client = fastly.connect(self.fastly_conf.apikey)

    def is_alive(self):
        """is_alive.

        :return boolean
        """
        response = requests.get(FASTLY_ENDPOINT)
        if response.status_code == 200:
            return True
        return False

    @property
    def provider_name(self):
        """provider name.

        :return 'Fastly'
        """
        return "Fastly"

    @property
    def client(self):
        """client to this provider.

        :return client
        """
        return self.fastly_client

    @property
    def service_controller(self):
        """Hook for service controller.

        :return service controller
        """
        return controllers.ServiceController(self)
