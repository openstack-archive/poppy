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
class HostBase(object):
    """This class is responsible for managing hostnames.
    Hostname operations include CRUD, etc.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def list(self, project=None, marker=None,
             limit=None, detailed=False):
        """Base method for listing hostnames.

        :param project: Project id
        :param marker: The last host name
        :param limit: (Default 10, configurable) Max number
            hostnames to return.
        :param detailed: Whether metadata is included

        :returns: An iterator giving a sequence of hostnames
            and the marker of the next page.
        """
        raise NotImplementedError
