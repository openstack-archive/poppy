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

from oslo_config import cfg

_PROVIDER_OPTIONS = [
    cfg.IntOpt(
        'default_cache_ttl',
        default=86400,
        help='Default ttl to be set, when no caching rules are specified'),
]

_PROVIDER_GROUP = 'drivers:provider'


@six.add_metaclass(abc.ABCMeta)
class ProviderDriverBase(object):
    """Interface definition for storage drivers.

    Data plane storage drivers are responsible for implementing the
    core functionality of the system.

    Connection information and driver-specific options are
    loaded from the config file.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo_config.ConfigOpts`
    """

    def __init__(self, conf):
        self._conf = conf
        self._conf.register_opts(_PROVIDER_OPTIONS, group=_PROVIDER_GROUP)

    @abc.abstractmethod
    def is_alive(self):
        """Check if provider is alive and return bool indicating the status.

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def provider_name(self):
        """Provider name.

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def service_controller(self):
        """Returns the driver's service controller.

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def certificate_controller(self):
        """Returns the driver's certificate controller.

        :raises NotImplementedError
        """
        raise NotImplementedError
