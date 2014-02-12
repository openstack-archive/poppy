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
import six

from cdn import transport
from cdn.transport import DriverBase
from wsgiref import simple_server


@six.add_metaclass(abc.ABCMeta)
class Driver(transport.DriverBase):

    def __init__(self, conf):
        super(DriverBase, self).__init__()

        self.app = None

    def listen(self):
        """Self-host using 'bind' and 'port' from the WSGI config group."""
        bind = '127.0.0.1'
        port = '8080'
        msgtmpl = (u'Serving on host %(bind)s:%(port)s')

        print(msgtmpl)

        httpd = simple_server.make_server(bind=bind,
                                          port=port,
                                          app=self.app)
        httpd.serve_forever()
