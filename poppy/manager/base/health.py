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

from poppy.manager.base import controller


@six.add_metaclass(abc.ABCMeta)
class HealthControllerBase(controller.ManagerControllerBase):
    """Health controller base class."""

    def __init__(self, manager):
        super(HealthControllerBase, self).__init__(manager)

        self._dns = self.driver.dns
        self._storage = self.driver.storage
        self._providers = self.driver.providers
        self._distributed_task = self.driver.distributed_task

    @abc.abstractmethod
    def health(self):
        """Returns the health of storage and providers

        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_provider_alive(self, provider_name):
        """Returns the health of provider

        :param provider_name
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_distributed_task_alive(self, distributed_task_name):
        """Returns the health of distributed_task

        :param distributed_task_name
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_dns_alive(self, dns_name):
        """Returns the health of DNS Provider

        :param dns_name
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_storage_alive(self, storage_name):
        """Returns the health of storage

        :param storage_name
        :raises: NotImplementedError
        """
        raise NotImplementedError
