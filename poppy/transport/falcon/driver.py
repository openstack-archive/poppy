# Copyright (c) 2013 Rackspace, Inc.
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

import abc
from wsgiref import simple_server

import falcon
from oslo.config import cfg
import six

import poppy.openstack.common.log as logging
from poppy import transport
from poppy.transport.falcon import services
from poppy.transport.falcon import v1


_WSGI_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),

    cfg.IntOpt('port', default=8888,
               help='Port on which the self-hosting server will listen'),

]

_WSGI_GROUP = 'drivers:transport:falcon'

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class TransportDriver(transport.Driver):

    def __init__(self, conf, manager):
        super(TransportDriver, self).__init__(conf, manager)

        self._conf.register_opts(_WSGI_OPTIONS, group=_WSGI_GROUP)
        self._wsgi_conf = self._conf[_WSGI_GROUP]

        self._setup_app()

    def _setup_app(self):
        """Initialize hooks and URI routes to resources."""
        self._app = falcon.API()
        version_path = "/v1.0"
        project_id = "/{project_id}"

        prefix = version_path + project_id

        # init the controllers
        service_controller = self.manager.services_controller

        # setup the routes
        self._app.add_route(prefix,
                            v1.V1Resource())

        self._app.add_route(prefix + '/services',
                            services.ServicesResource(service_controller))

        self._app.add_route(prefix + '/services/{service_name}',
                            services.ServiceResource(service_controller))

    def listen(self):
        """Self-host using 'bind' and 'port' from the WSGI config group."""
        msgtmpl = (u'Serving on host %(bind)s:%(port)s')
        LOG.info(msgtmpl,
                 {'bind': self._wsgi_conf.bind, 'port': self._wsgi_conf.port})

        httpd = simple_server.make_server(self._wsgi_conf.bind,
                                          self._wsgi_conf.port,
                                          self.app)
        httpd.serve_forever()
