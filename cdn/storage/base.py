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

import abc
import six

from oslo.config import cfg

_LIMITS_OPTIONS = [
    cfg.IntOpt('default_services_paging', default=10,
               help='Default services pagination size')
]

_LIMITS_GROUP = 'limits:storage'


@six.add_metaclass(abc.ABCMeta)
class DriverBase(object):
    """Base class for both data and control plane drivers

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo.config.ConfigOpts`
    """
    def __init__(self, conf, providers):
        self.conf = conf
        self.providers = providers

    def providers(self):
        return self.providers


@six.add_metaclass(abc.ABCMeta)
class StorageDriverBase(DriverBase):
    """Interface definition for storage drivers.

    Data plane storage drivers are responsible for implementing the
    core functionality of the system.

    Connection information and driver-specific options are
    loaded from the config file.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo.config.ConfigOpts`
    """

    def __init__(self, conf, providers):
        super(StorageDriverBase, self).__init__(conf, providers)

        self.conf.register_opts(_LIMITS_OPTIONS, group=_LIMITS_GROUP)
        self.limits_conf = self.conf[_LIMITS_GROUP]

    @abc.abstractmethod
    def is_alive(self):
        """Check whether the storage is ready."""
        raise NotImplementedError

    @abc.abstractproperty
    def service_controller(self):
        """Returns the driver's hostname controller."""
        raise NotImplementedError


class ControllerBase(object):
    """Top-level class for controllers.

    :param driver: Instance of the driver
        instantiating this controller.
    """

    def __init__(self, driver):
        self.driver = driver


@six.add_metaclass(abc.ABCMeta)
class ServicesBase(ControllerBase):
    """This class is responsible for managing Services
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, driver):
        super(ServicesBase, self).__init__(driver)

        self.wrapper = ProviderWrapper()

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError
        
    @abc.abstractmethod
    def create(self, service_name, service_json):
        return self.driver.providers.map(self.wrapper.create, service_name, service_json)

    @abc.abstractmethod
    def update(self, service_name):
        return self.driver.providers.map(self.wrapper.update, service_name)

    @abc.abstractmethod
    def delete(self, service_name):
        return self.driver.providers.map(self.wrapper.delete, service_name)

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError


class ProviderWrapper(object):

    def create(self, ext, service_name, service_json):
        return ext.obj.service_controller.create(service_name, service_json)

    def update(self, ext, service_name):
        return ext.obj.service_controller.update(service_name)

    def delete(self, ext, service_name):
        return ext.obj.service_controller.delete(service_name)


