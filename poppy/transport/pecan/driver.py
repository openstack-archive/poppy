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

from wsgiref import simple_server

from oslo.config import cfg
import pecan

from poppy.openstack.common import log
from poppy import transport
from poppy.transport.pecan import controllers
from poppy.transport.pecan.controllers import v1
from poppy.transport.pecan import hooks


_PECAN_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),
    cfg.IntOpt('port', default=8888,
               help='Port on which the self-hosting server will listen'),
]

_PECAN_GROUP = 'drivers:transport:pecan'

LOG = log.getLogger(__name__)


class PecanTransportDriver(transport.Driver):

    def __init__(self, conf, manager):

        super(PecanTransportDriver, self).__init__(conf, manager)

        self._conf.register_opts(_PECAN_OPTIONS, group=_PECAN_GROUP)
        self._pecan_conf = self._conf[_PECAN_GROUP]

        self._setup_app()

    def _setup_app(self):
        root_controller = controllers.Root(self)

        home_controller = v1.Home(self)

        root_controller.add_controller('v1.0', home_controller)

        home_controller.add_controller('ping', v1.Ping(self))
        health_controller = v1.Health(self)
        home_controller.add_controller('health', health_controller)
        health_controller.add_controller('storage', v1.StorageHealth(self))
        health_controller.add_controller('provider', v1.ProviderHealth(self))
        home_controller.add_controller('services', v1.Services(self))
        home_controller.add_controller('flavors', v1.Flavors(self))

        pecan_hooks = [hooks.Context()]
        self._app = pecan.make_app(root_controller, hooks=pecan_hooks)

    def listen(self):
        LOG.info(
            'Serving on host %(bind)s:%(port)s',
            {
                'bind': self._pecan_conf.bind,
                'port': self._pecan_conf.port,
            },
        )

        httpd = simple_server.make_server(self._pecan_conf.bind,
                                          self._pecan_conf.port,
                                          self.app)
        httpd.serve_forever()
