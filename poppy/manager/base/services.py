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
from poppy.manager.base import providers


@six.add_metaclass(abc.ABCMeta)
class ServicesControllerBase(controller.ManagerControllerBase):
    """Services controller base class."""

    def __init__(self, manager):
        super(ServicesControllerBase, self).__init__(manager)

        self.provider_wrapper = providers.ProviderWrapper()

    @abc.abstractmethod
    def list(self, project_id, marker=None, limit=None):
        """list

        :param project_id
        :param marker
        :limit
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, project_id, service_id):
        """GET

        :param project_id
        :param service_id
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, project_id, service_obj):
        """create

        :param project_id
        :param service_obj
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, project_id, service_id, service_obj):
        """POST

        :param project_id
        :param service_id
        :param service_obj
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, project_id, service_id):
        """DELETE

       :param project_id
       :param service_id
       :raises: NotImplementedError
       """
        raise NotImplementedError

    @abc.abstractmethod
    def purge(self, project_id, service_id, purge_url=None):
        '''If purge_url is none, all content of this service will be purge.'''
        raise NotImplementedError
