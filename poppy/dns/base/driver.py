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
class DNSDriverBase(object):
    """Interface definition for dns drivers.

    DNS drivers are responsible for creating CNAME records in a DNS records
    for an operator.  Thus allowing the operator to abstract away the
    underlying CDN provider used by customers of the API.

    Use the Default DNS driver if you just want to pass through and not
    use the CNAME capabilities of a DNS provider to mask the underlying
    CDN provider url.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo_config.ConfigOpts`
    """

    def __init__(self, conf):
        self._conf = conf

    @abc.abstractmethod
    def is_alive(self):
        """Check whether the dns provider is ready.

        :raises NotImplementedError
        """

        raise NotImplementedError

    @abc.abstractproperty
    def dns_name(self):
        """Name of this provider.

        :raises NotImplementedError
        """

        raise NotImplementedError

    @property
    def client(self):
        """Client for this provider.

        :raises NotImplementedError
        """

        raise NotImplementedError

    @abc.abstractproperty
    def services_controller(self):
        """Returns the driver's hostname controller.

         :raises NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractproperty
    def retry_exceptions(self):
        """Retry on certain exceptions.

         :raises NotImplementedError
        """
        raise NotImplementedError
