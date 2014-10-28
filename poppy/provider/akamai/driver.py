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

"""Akamai CDN Provider implementation."""

from akamai import edgegrid
from oslo.config import cfg
import requests

from poppy.provider import base
from poppy.provider.akamai import controllers

AKAMAI_OPTIONS = [
    cfg.StrOpt('client_token', help='Akamai client token'),
    cfg.StrOpt('client_secret', help='Akamai client secret'),
    cfg.StrOpt('access_token', help='Akamai access token'),
    cfg.StrOpt('base_url', help='Akamai API base URL'),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class CDNProvider(base.Driver):
    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(AKAMAI_OPTIONS,
                                 group=AKAMAI_GROUP)
        self.akamai_conf = self._conf[AKAMAI_GROUP]
        self.akamai_base_url = self.akamai_conf.base_url

        self.akamai_client = requests.Session()
        self.akamai_client.auth = edgegrid.EdgeGridAuth(
            client_token=self.akamai_conf.client_token,
            client_secret=self.akamai_conf.client_secret,
            access_token=self.akamai_conf.access_token
        )

    def is_alive(self):
        return True

    @property
    def provider_name(self):
        return "Akamai"

    @property
    def client(self):
        return self.akamai_client

    @property
    def service_controller(self):
        """Returns the driver's hostname controller."""
        return controllers.ServiceController(self)
