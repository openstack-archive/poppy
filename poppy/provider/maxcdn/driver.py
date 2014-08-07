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

"""Max CDN Provider implementation."""

import maxcdn
from oslo.config import cfg

from poppy.openstack.common import log as logging
from poppy.provider import base
from poppy.provider.maxcdn import controllers


LOG = logging.getLogger(__name__)

MAXCDN_OPTIONS = [
    cfg.StrOpt('alias', help='MAXCDN API account alias'),
    cfg.StrOpt('consumer_key', help='MAXCDN API consumer key'),
    cfg.StrOpt('consumer_secret', help='MAXCDN API consumer secret'),
]

MAXCDN_GROUP = 'drivers:provider:maxcdn'


class CDNProvider(base.Driver):

    def __init__(self, conf):
        """Init constructor."""
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(MAXCDN_OPTIONS,
                                 group=MAXCDN_GROUP)
        self.maxcdn_conf = self._conf[MAXCDN_GROUP]

        self.maxcdn_client = maxcdn.MaxCDN(self.maxcdn_conf.alias,
                                           self.maxcdn_conf.consumer_key,
                                           self.maxcdn_conf.consumer_secret)

    def is_alive(self):
        """For health state."""
        return True

    @property
    def provider_name(self):
        """For name."""
        return "MaxCDN"

    @property
    def client(self):
        """client to this provider."""
        return self.maxcdn_client

    @property
    def service_controller(self):
        """Hook for service controller."""
        return controllers.ServiceController(self)
