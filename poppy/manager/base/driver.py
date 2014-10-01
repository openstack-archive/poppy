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


@six.add_metaclass(abc.ABCMeta)
class ManagerDriverBase(object):
    """Base class for driver manager."""

    def __init__(self, conf, storage, providers):
        self._conf = conf
        self._storage = storage
        self._providers = providers

    @property
    def storage(self):
        """storage

        :param self
        :returns storage
        """
        return self._storage

    @property
    def providers(self):
        """storage

        :param self
        :returns providers
        """
        return self._providers

    @abc.abstractproperty
    def services_controller(self):
        """Returns the driver's services controller

        :param self
        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def flavors_controller(self):
        """Returns the driver's flavors controller

        :param self
        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def health_controller(self):
        """Returns the driver's health controller

        :param self
        :raises NotImplementedError
        """
        raise NotImplementedError
