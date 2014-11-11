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

from oslo.config import cfg
from stevedore import driver
from stevedore import named

from poppy.common import decorators
from poppy.openstack.common import log


LOG = log.getLogger(__name__)

_DEFAULT_OPTIONS = [
    cfg.StrOpt('datacenter', default='',
               help='Host datacenter of the API')
]

_DRIVER_OPTIONS = [
    cfg.StrOpt('transport', default='pecan',
               help='Transport driver to use'),
    cfg.StrOpt('manager', default='default',
               help='Manager driver to use'),
    cfg.StrOpt('storage', default='mockdb',
               help='Storage driver to use'),
    cfg.ListOpt('providers', default=['mock'],
                help='Provider driver(s) to use'),
    cfg.StrOpt('dns', default='default',
               help='DNS driver to use'),
]

_DRIVER_GROUP = 'drivers'


class Bootstrap(object):

    """Defines the CDN bootstrapper.

    The bootstrap loads up drivers per a given configuration, and
    manages their lifetimes.
    """

    def __init__(self, conf):
        self.conf = conf
        self.conf.register_opts(_DEFAULT_OPTIONS)
        self.conf.register_opts(_DRIVER_OPTIONS, group=_DRIVER_GROUP)
        self.driver_conf = self.conf[_DRIVER_GROUP]

        log.setup('poppy')

        LOG.debug("init bootstrap")

    @decorators.lazy_property(write=False)
    def dns(self):
        """DNS."""

        LOG.debug((u'Loading DNS driver'))

        # create the driver manager to load the appropriate drivers
        dns_type = 'poppy.dns'
        dns_name = self.driver_conf.dns

        args = [self.conf]

        try:
            mgr = driver.DriverManager(namespace=dns_type,
                                       name=dns_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    @decorators.lazy_property(write=False)
    def provider(self):
        """provider.

        :returns mgr
        """

        LOG.debug((u'Loading provider extension(s)'))

        # create the driver manager to load the appropriate drivers
        provider_type = 'poppy.provider'
        args = [self.conf]
        provider_names = self.driver_conf.providers

        mgr = named.NamedExtensionManager(namespace=provider_type,
                                          names=provider_names,
                                          invoke_on_load=True,
                                          invoke_args=args)
        return mgr

    @decorators.lazy_property(write=False)
    def storage(self):
        """storage.

        :returns mgr driver
        """

        LOG.debug((u'Loading storage driver'))

        # create the driver manager to load the appropriate drivers
        storage_type = 'poppy.storage'
        storage_name = self.driver_conf.storage

        args = [self.conf]

        try:
            mgr = driver.DriverManager(namespace=storage_type,
                                       name=storage_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    @decorators.lazy_property(write=False)
    def manager(self):
        """manager.

        :returns mgr driver
        """
        LOG.debug((u'Loading manager driver'))

        # create the driver manager to load the appropriate drivers
        manager_type = 'poppy.manager'
        manager_name = self.driver_conf.manager

        args = [self.conf, self.storage, self.provider, self.dns]

        try:
            mgr = driver.DriverManager(namespace=manager_type,
                                       name=manager_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    @decorators.lazy_property(write=False)
    def transport(self):
        """transport.

        :returns mgr driver
        """
        LOG.debug("loading transport")

        # create the driver manager to load the appropriate drivers
        transport_type = 'poppy.transport'
        transport_name = self.driver_conf.transport

        args = [self.conf, self.manager]

        LOG.debug((u'Loading transport driver: %s'), transport_name)

        try:
            mgr = driver.DriverManager(namespace=transport_type,
                                       name=transport_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    def run(self):
        self.transport.listen()
