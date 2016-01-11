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
    def __init__(self, conf, storage, providers, dns, distributed_task,
                 notification, metrics):
        self._conf = conf
        self._storage = storage
        self._providers = providers
        self._dns = dns
        self._distributed_task = distributed_task
        self._notification = notification
        self._metrics = metrics

    @property
    def conf(self):
        """conf

        :returns conf
        """
        return self._conf

    @property
    def storage(self):
        """storage

        :returns storage
        """
        return self._storage

    @property
    def providers(self):
        """providers

        :returns providers
        """
        return self._providers

    @property
    def dns(self):
        return self._dns

    @property
    def distributed_task(self):
        return self._distributed_task

    @property
    def notification(self):
        return self._notification

    @property
    def metrics(self):
        return self._metrics

    @abc.abstractproperty
    def analytics_controller(self):
        """Returns the driver's analytics controller

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def services_controller(self):
        """Returns the driver's services controller

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def flavors_controller(self):
        """Returns the driver's flavors controller

        :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def health_controller(self):
        """Returns the driver's health controller

        :raises NotImplementedError
        """
        raise NotImplementedError
