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
class TransportDriverBase(object):
    """Base class for Transport Drivers to document the expected interface.

    :param conf: configuration instance
    :type conf: oslo_config.cfg.CONF
    """

    def __init__(self, conf, manager):
        self._conf = conf
        self._manager = manager

        self._app = None

    @property
    def app(self):
        """Get app.

        :returns app
        """
        return self._app

    @property
    def conf(self):
        """Get conf.

        :returns conf
        """
        return self._conf

    @property
    def manager(self):
        """Get manager

        :returns manager
        """
        return self._manager

    @abc.abstractmethod
    def listen(self):
        """Start listening for client requests (self-hosting mode).

        :raises NotImplementedError
        """
        raise NotImplementedError
