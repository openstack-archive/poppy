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
class HomeControllerBase(controller.ManagerControllerBase):
    """Home controller base class."""

    def __init__(self, manager):
        super(HomeControllerBase, self).__init__(manager)

    @abc.abstractmethod
    def get(self):
        """get

        :param self
        :raises: NotImplementedError
        """
        raise NotImplementedError
