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

"""DNS Provider implementation."""

from oslo.config import cfg

from poppy.dns import base
from poppy.dns.rackspace import controllers
from poppy.openstack.common import log as logging


RACKSPACE_OPTIONS = [
    cfg.StrOpt('project_id', default='',
               help='Keystone Project ID'),
    cfg.StrOpt('api_key', default='',
               help='Keystone API Key'),
    cfg.BoolOpt('sharding_enabled', default=True,
                help='Enable Sharding?'),
    cfg.IntOpt('num_shards', default=10, help='Number of Shards to use'),
    cfg.StrOpt('shard_prefix', default='cdn',
               help='The shard prefix to use'),
    cfg.StrOpt('url', default='',
               help='The url for customers to CNAME to'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'

LOG = logging.getLogger(__name__)


class DNSProvider(base.Driver):

    def __init__(self, conf):
        super(DNSProvider, self).__init__(conf)

    def is_alive(self):
        return True

    @property
    def dns_name(self):
        return "Rackspace Cloud DNS"

    @property
    def service_controller(self):
        return controllers.ServiceController(self)
