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
import json
import traceback
import six
import sys

from oslo.config import cfg

_LIMITS_OPTIONS = [
    cfg.IntOpt('default_services_paging', default=10,
               help='Default services pagination size')
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
    def service_controller(self):
        """Returns the extension's hostname controller."""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class ServiceBase(object):
    """This class is responsible for managing services.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self):
        raise NotImplementedError

class ProviderResponse(object):
    def __init__(self, provider_type):
        self.provider = provider_type

    def failed(self, msg):
        ex_type, ex, tb = sys.exc_info()

        print "error: ", self.provider, msg, ex_type, ex
        traceback.print_tb(tb)

        return { 
            self.provider: { 
                "error" : msg 
            } 
        }

    def created(self, domain):
        return { 
            self.provider : { 
                "domain": domain
            } 
        }
        
    def updated(self, domain):
        return { 
            self.provider : { 
                "domain": domain
            } 
        }

    def deleted(self, domain):
        return { 
            self.provider : { 
                "domain": domain
            } 
        }
        



  