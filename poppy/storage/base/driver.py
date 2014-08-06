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
class StorageDriverBase(object):
    """Interface definition for storage drivers.

    Data plane storage drivers are responsible for implementing the
    core functionality of the system.

    Connection information and driver-specific options are
    loaded from the config file.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo.config.ConfigOpts`
    """

    def __init__(self, conf):
        self._conf = conf
        self._conf.register_opts(_LIMITS_OPTIONS, group=_LIMITS_GROUP)
        self.limits_conf = self._conf[_LIMITS_GROUP]

    @abc.abstractmethod
    def is_alive(self):
        """Check whether the storage is ready."""
        raise NotImplementedError

    @abc.abstractproperty
    def service_controller(self):
        """Returns the driver's hostname controller."""
        raise NotImplementedError
