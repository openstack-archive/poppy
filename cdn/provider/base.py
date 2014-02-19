# Copyright (c) 2013 Rackspace, Inc.
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

from oslo.config import cfg

_LIMITS_OPTIONS = [
    cfg.IntOpt('default_hostname_paging', default=10,
               help='Default hostname pagination size')
]

_LIMITS_GROUP = 'limits:storage'


@six.add_metaclass(abc.ABCMeta)
class ProviderBase(object):
    """Base class for CDN Provider extensions

    :param conf: Configuration containing options for this extension.
    :type conf: `oslo.config.ConfigOpts`
    """
    def __init__(self, conf):
        self.conf = conf


@six.add_metaclass(abc.ABCMeta)
class CDNProviderBase(ProviderBase):
    """Interface definition for CDN Provider Extensions.

    CDN Provider extensions are responsible for implementing the
    communication with the CDN Network and Edge nodes.

    Connection information and driver-specific options are
    loaded from the config file.

    :param conf: Configuration containing options for this extension.
    :type conf: `oslo.config.ConfigOpts`
    """

    def __init__(self, conf):
        super(CDNProviderBase, self).__init__(conf)

        self.conf.register_opts(_LIMITS_OPTIONS, group=_LIMITS_GROUP)
        self.limits_conf = self.conf[_LIMITS_GROUP]

    @abc.abstractmethod
    def is_alive(self):
        """Check whether the provider is ready."""
        raise NotImplementedError

    @abc.abstractproperty
    def host_controller(self):
        """Returns the extension's hostname controller."""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class HostBase(object):
    """This class is responsible for managing hostnames.
    Hostname operations include CRUD, etc.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError
