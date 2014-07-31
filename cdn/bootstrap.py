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

from cdn.common import decorators
from cdn.openstack.common import log
from oslo.config import cfg
from stevedore import driver, extension


LOG = log.getLogger(__name__)


_DRIVER_OPTIONS = [
    cfg.StrOpt('transport', default='pecan',
               help='Transport driver to use'),
    cfg.StrOpt('manager', default='default',
               help='Manager driver to use'),
    cfg.StrOpt('storage', default='mockdb',
               help='Storage driver to use'),
]

_DRIVER_GROUP = 'drivers'


class Bootstrap(object):
    """Defines the CDN bootstrapper.

    The bootstrap loads up drivers per a given configuration, and
    manages their lifetimes.
    """

    def __init__(self, conf):
        self.conf = conf
        self.conf.register_opts(_DRIVER_OPTIONS, group=_DRIVER_GROUP)
        self.driver_conf = self.conf[_DRIVER_GROUP]

        log.setup('cdn')

        LOG.debug("init bootstrap")

    @decorators.lazy_property(write=False)
    def provider(self):
        LOG.debug((u'Loading provider extension(s)'))

        # create the driver manager to load the appropriate drivers
        provider_type = 'cdn.provider'
        args = [self.conf]

        try:
            mgr = extension.ExtensionManager(namespace=provider_type,
                                             invoke_on_load=True,
                                             invoke_args=args)
            return mgr
        except RuntimeError as exc:
            LOG.exception(exc)

    @decorators.lazy_property(write=False)
    def storage(self):
        LOG.debug((u'Loading storage driver'))

        # create the driver manager to load the appropriate drivers
        storage_type = 'cdn.storage'
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
        LOG.debug((u'Loading manager driver'))

        # create the driver manager to load the appropriate drivers
        manager_type = 'cdn.manager'
        manager_name = self.driver_conf.manager

        args = [self.conf, self.storage, self.provider]

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
        LOG.debug("loading transport")

        # create the driver manager to load the appropriate drivers
        transport_type = 'cdn.transport'
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
