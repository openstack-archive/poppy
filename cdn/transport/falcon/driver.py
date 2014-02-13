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

import cdn.openstack.common.log as logging
from cdn import transport
from cdn.transport.falcon import (
    v1, hosts
)


_WSGI_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),

    cfg.IntOpt('port', default=8888,
               help='Port on which the self-hosting server will listen'),

]

_WSGI_GROUP = 'drivers:transport:falcon'

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class TransportDriver(transport.DriverBase):

    def __init__(self, conf):
        super(TransportDriver, self).__init__(conf)

        self._conf.register_opts(_WSGI_OPTIONS, group=_WSGI_GROUP)
        self._wsgi_conf = self._conf[_WSGI_GROUP]

        self.app = None
        self._init_routes()

    def _init_routes(self):
        """Initialize hooks and URI routes to resources."""
        self.app = falcon.API()
        version_path = "/v1"

        self.app.add_route(version_path, v1.V1Resource())
        self.app.add_route(version_path + '/hosts', hosts.HostsResource())

    def listen(self):
        """Self-host using 'bind' and 'port' from the WSGI config group."""
        msgtmpl = (u'Serving on host %(bind)s:%(port)s')
        LOG.info(msgtmpl,
                 {'bind': self._wsgi_conf.bind, 'port': self._wsgi_conf.port})

        httpd = simple_server.make_server(self._wsgi_conf.bind,
                                          self._wsgi_conf.port,
                                          self.app)
        httpd.serve_forever()
