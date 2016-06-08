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
from poppy.manager.base import notifications
from poppy.manager.base import providers


@six.add_metaclass(abc.ABCMeta)
class ServicesControllerBase(controller.ManagerControllerBase):
    """Services controller base class."""

    def __init__(self, manager):
        super(ServicesControllerBase, self).__init__(manager)

        self.provider_wrapper = providers.ProviderWrapper()
        self.notification_wrapper = notifications.NotificationWrapper()

    @abc.abstractmethod
    def get_services(self, project_id, marker=None, limit=None):
        """Get a list of services.

        :param project_id
        :param marker
        :param limit
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_service(self, project_id, service_id):
        """Get a service.

        :param project_id
        :param service_id
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_service(self, project_id, auth_token, service_obj):
        """Create a service.

        :param project_id
        :param auth_token
        :param service_obj
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_service(self, project_id, service_id,
                       auth_token, service_updates, force_update=False):
        """Update a service.

        :param project_id
        :param service_id
        :param auth_token
        :param service_updates
        :param force_update
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def services_action(self, project_id, action, domain=None):
        """services_action

        :param project_id
        :param action
        :param domain
        :raises ValueError
        """

    @abc.abstractmethod
    def delete_service(self, project_id, service_id):
        """Delete a service.

       :param project_id
       :param service_id
       :raises: NotImplementedError
       """
        raise NotImplementedError

    @abc.abstractmethod
    def purge(self, project_id, service_id, hard=False, purge_url=None):
        """Purge assets for a service.

        If purge_url is none, all content of this service will be purged.

        :param project_id
        :param service_id
        :param hard
        :param purge_url
        """
        raise NotImplementedError
