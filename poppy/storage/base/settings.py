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
class SettingsControllerBase(controller.StorageControllerBase):
    """Settings Controller Base definition."""

    def __init__(self, driver):
        super(SettingsControllerBase, self).__init__(driver)

    @abc.abstractmethod
    def get_san_cert_hostname_limit(self):
        """Get the san cert hostname limit setting.

        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_san_cert_hostname_limit(self, limit):
        """Update the san cert hostname limit setting.

        :param limit: the new limit
        :raise NotImplementedError
        """
        raise NotImplementedError
