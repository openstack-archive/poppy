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

from oslo_config import cfg
from oslo_log import log
import pyrax

from poppy.dns import base
from poppy.dns.rackspace import controllers
from poppy.dns.rackspace.helpers import retry_exceptions


RACKSPACE_OPTIONS = [
    cfg.StrOpt('username', default='',
               help='Keystone Username'),
    cfg.StrOpt('api_key', default='',
               help='Keystone API Key'),
    cfg.BoolOpt('sharding_enabled', default=True,
                help='Enable Sharding?'),
    cfg.IntOpt('num_shards', default=10, help='Number of Shards to use'),
    cfg.StrOpt('shard_prefix', default='cdn',
               help='The shard prefix to use'),
    cfg.IntOpt('shared_ssl_num_shards', default=5, help='Number of Shards '
               'to use in generating shared ssl domain suffix'),
    cfg.StrOpt('shared_ssl_shard_prefix', default='scdn',
               help='The shard prefix to use '
               'in generating shared ssl domain suffix'),
    cfg.StrOpt('shared_ssl_domain_suffix', default='',
               help='The shared ssl domain suffix to generate'
               ' shared ssl domain'),
    cfg.StrOpt('url', default='',
               help='The url for customers to CNAME to'),
    cfg.StrOpt('email', help='The email to be provided to Rackspace DNS for'
               'creating subdomains'),
    cfg.StrOpt('auth_endpoint', default='',
               help='Authentication end point for DNS'),
    cfg.IntOpt('timeout', default=30, help='DNS response timeout'),
    cfg.IntOpt('delay', default=1, help='DNS retry delay'),
    cfg.StrOpt('url_404', default='',
               help='The url to CNAME to when a service is disabled'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'

LOG = log.getLogger(__name__)


class DNSProvider(base.Driver):
    """Rackspace DNS Provider."""

    def __init__(self, conf):
        super(DNSProvider, self).__init__(conf)

        self._conf.register_opts(RACKSPACE_OPTIONS, group=RACKSPACE_GROUP)
        self.rackdns_conf = self._conf[RACKSPACE_GROUP]
        if self.rackdns_conf.auth_endpoint:
            pyrax.set_setting("auth_endpoint", self.rackdns_conf.auth_endpoint)
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_credentials(self.rackdns_conf.username,
                              self.rackdns_conf.api_key)
        self.rackdns_client = pyrax.cloud_dns
        self.rackdns_client.set_timeout(self.rackdns_conf.timeout)
        self.rackdns_client.set_delay(self.rackdns_conf.delay)

    def is_alive(self):
        """is_alive.

        :return boolean
        """

        try:
            self.rackdns_client.list()
        except Exception:
            return False
        return True

    @property
    def dns_name(self):
        """DNS provider name.

        :return 'Rackspace Cloud DNS'
        """

        return 'Rackspace_Cloud_DNS'

    @property
    def client(self):
        """Client to this provider.

        :return client
        """

        return self.rackdns_client

    @property
    def services_controller(self):
        """Hook for service controller.

        :return service_controller
        """

        return controllers.ServicesController(self)

    @property
    def retry_exceptions(self):
        """Retry on certain exceptions.

        :return list
        """
        return retry_exceptions
