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

from poppy.storage.base import controller


@six.add_metaclass(abc.ABCMeta)
class ServicesControllerBase(controller.StorageControllerBase):
    """Services Controller Base definition."""

    def __init__(self, driver):
        super(ServicesControllerBase, self).__init__(driver)

    @abc.abstractmethod
    def list(self, project_id, marker=None, limit=None):
        """list

        :param project_id
        :param marker
        :param limit
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, project_id, service_id, service_json):
        """create

        :param project_id
        :param service_id
        :param service_json
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, project_id, service_id, service_json):
        """update

        :param project_id
        :param service_id
        :param service_json
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, project_id, service_id):
        """delete

        :param project_id
        :param service_id
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self):
        """get

        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_provider_details(self, project_id, service_id):
        """get_provider_details

        :param project_id
        :param service_id
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_provider_details(self, provider_details):
        """update_provider_details

        :param provider_details
        :raise NotImplementedError
        """
        raise NotImplementedError

    @staticmethod
    def format_result(result):
        """format_result

        :param result
        :raise NotImplementedError
        """
        raise NotImplementedError
