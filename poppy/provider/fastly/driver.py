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
from oslo_config import cfg
from oslo_log import log
import requests

from poppy.provider import base
from poppy.provider.fastly import controllers

LOG = log.getLogger(__name__)

FASTLY_OPTIONS = [
    cfg.StrOpt('apikey', help='Fastly API Key'),
    cfg.StrOpt('host', default='api.fastly.com', help='Fastly Host'),
    cfg.StrOpt('scheme', default='https',
               help='Fastly Scheme - HTTP (or) HTTPS'),
]

FASTLY_GROUP = 'drivers:provider:fastly'


class CDNProvider(base.Driver):
    """Fastly CNDProvider."""

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(FASTLY_OPTIONS,
                                 group=FASTLY_GROUP)
        self.fastly_conf = self._conf[FASTLY_GROUP]

        # Override the hardcoded values in the fastly client with
        # values defined in poppy.conf.
        module_name = 'fastly'
        fastly_host = 'FASTLY_HOST'
        fastly_scheme = 'FASTLY_SCHEME'
        obj = globals()[module_name]
        setattr(obj, fastly_host, self.fastly_conf.host)
        setattr(obj, fastly_scheme, self.fastly_conf.scheme)

        self.fastly_client = fastly.connect(self.fastly_conf.apikey)
        self.regions = []

    def is_alive(self):
        """is_alive.

        :return boolean
        """
        fastly_url = self.fastly_conf.scheme + '://' + self.fastly_conf.host
        response = requests.get(fastly_url)
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

    @property
    def certificate_controller(self):
        """Hook for certificate controller.

        :return certificate controller
        """
        return controllers.CertificateController(self)
