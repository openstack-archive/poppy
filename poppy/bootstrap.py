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

from oslo_config import cfg
from oslo_log import log
from stevedore import driver
from stevedore import named

from poppy.common import decorators


LOG = log.getLogger(__name__)

_CLI_OPTIONS = (
    cfg.BoolOpt('daemon', default=False,
                help='Run Poppy server in the background.'),
)

# NOTE (Obulpathi): Register daemon command line option for
# poppy-server
CONF = cfg.CONF
CONF.register_cli_opts(_CLI_OPTIONS)


_DEFAULT_OPTIONS = [
    cfg.StrOpt('datacenter', default='',
               help='Host datacenter of the API'),
    cfg.BoolOpt('project_id_in_url', default=False,
                help='Indicating if the project id'
                ' should be presented in the url')
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
    cfg.ListOpt('notifications', default=['mail'],
                help='Notification driver(s) to use'),
    cfg.StrOpt('dns', default='default',
               help='DNS driver to use'),
    cfg.StrOpt('distributed_task', default='taskflow',
               help='distributed_task driver to use'),
    cfg.StrOpt('metrics', default='blueflood',
               help='metrics driver to use'),
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
    def notification(self):
        """notification.

        :returns mgr
        """

        LOG.debug((u'Loading notification extension(s)'))

        # create the driver manager to load the appropriate drivers
        notification_type = 'poppy.notification'
        args = [self.conf]
        notification_type_names = self.driver_conf.notifications

        mgr = named.NamedExtensionManager(namespace=notification_type,
                                          names=notification_type_names,
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

        args = [self.conf, self.storage, self.provider, self.dns,
                self.distributed_task, self.notification, self.metrics]

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

    @decorators.lazy_property(write=False)
    def distributed_task(self):
        """distributed task driver.

        :returns distributed task driver
        """
        LOG.debug("loading distributed task")

        # create the driver manager to load the appropriate drivers
        distributed_task_type = 'poppy.distributed_task'
        distributed_task_name = self.driver_conf.distributed_task

        args = [self.conf]

        LOG.debug((u'Loading distributed_task driver: %s'),
                  distributed_task_name)

        try:
            mgr = driver.DriverManager(namespace=distributed_task_type,
                                       name=distributed_task_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    @decorators.lazy_property(write=False)
    def metrics(self):
        """metrics driver.

        :returns metrics driver
        """
        LOG.debug("loading metrics driver")

        # create the driver manager to load the appropriate drivers
        metrics_driver_type = 'poppy.metrics'
        metrics_driver_name = self.driver_conf.metrics

        args = [self.conf]

        LOG.debug((u'Loading metrics driver: %s'),
                  metrics_driver_name)

        try:
            mgr = driver.DriverManager(namespace=metrics_driver_type,
                                       name=metrics_driver_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            LOG.exception(exc)

    def run(self):
        self.transport.listen()
