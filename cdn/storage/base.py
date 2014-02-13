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

from oslo.config import cfg

_LIMITS_OPTIONS = [
    cfg.IntOpt('default_hostname_paging', default=10,
               help='Default hostname pagination size')
]

_LIMITS_GROUP = 'limits:storage'


@six.add_metaclass(abc.ABCMeta)
class DriverBase(object):
    """Base class for both data and control plane drivers

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo.config.ConfigOpts`
    :param cache: Cache instance to use for reducing latency
        for certain lookups.
    :type cache: `cdn.common.cache.backends.BaseCache`
    """
    def __init__(self, conf, cache):
        self.conf = conf
        self.cache = cache


@six.add_metaclass(abc.ABCMeta)
class StorageDriverBase(DriverBase):
    """Interface definition for storage drivers.

    Data plane storage drivers are responsible for implementing the
    core functionality of the system.

    Connection information and driver-specific options are
    loaded from the config file.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo.config.ConfigOpts`
    :param cache: Cache instance to use for reducing latency
        for certain lookups.
    :type cache: `cdn.common.cache.backends.BaseCache`
    """

    def __init__(self, conf, cache):
        super(StorageDriverBase, self).__init__(conf, cache)

        self.conf.register_opts(_LIMITS_OPTIONS, group=_LIMITS_GROUP)
        self.limits_conf = self.conf[_LIMITS_GROUP]

    @abc.abstractmethod
    def is_alive(self):
        """Check whether the storage is ready."""
        raise NotImplementedError

    @abc.abstractproperty
    def host_controller(self):
        """Returns the driver's hostname controller."""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class HostBase(object):
    """This class is responsible for managing hostnames.
    Hostname operations include CRUD, etc.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def list(self, project=None, marker=None,
             limit=None, detailed=False):
        """Base method for listing hostnames.

        :param project: Project id
        :param marker: The last host name
        :param limit: (Default 10, configurable) Max number
            hostnames to return.
        :param detailed: Whether metadata is included

        :returns: An iterator giving a sequence of hostnames
            and the marker of the next page.
        """
        raise NotImplementedError
