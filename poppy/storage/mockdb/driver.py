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

"""Storage driver implementation."""

from oslo_config import cfg
from oslo_log import log

from poppy.storage import base
from poppy.storage.mockdb import controllers


LOG = log.getLogger(__name__)

MOCKDB_OPTIONS = [
    cfg.StrOpt('database', default='poppy',
               help='Database for all queries made in session')
]

MOCKDB_GROUP = 'drivers:storage:mockdb'


def _connection():
    return None


class MockDBStorageDriver(base.Driver):

    def __init__(self, conf):
        super(MockDBStorageDriver, self).__init__(conf)

        self._conf.register_opts(MOCKDB_OPTIONS,
                                 group=MOCKDB_GROUP)
        self.mockdb_conf = self._conf[MOCKDB_GROUP]

    def is_alive(self):
        return True

    @property
    def storage_name(self):
        """For name."""
        return 'MockDB'

    @property
    def connection(self):
        """Connection instance."""
        return _connection()

    @property
    def certificates_controller(self):
        return controllers.CertificatesController(self)

    @property
    def flavors_controller(self):
        return controllers.FlavorsController(self)

    @property
    def services_controller(self):
        return controllers.ServicesController(self)

    @property
    def database(self):
        return self.connection

    def connect(self):
        return ""

    def close_connection(self):
        return None
