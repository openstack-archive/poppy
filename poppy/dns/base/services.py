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

from poppy.dns.base import controller
from poppy.dns.base import responder


@six.add_metaclass(abc.ABCMeta)
class ServicesControllerBase(controller.DNSControllerBase):

    """Services Controller Base class."""

    def __init__(self, driver):
        super(ServicesControllerBase, self).__init__(driver)

        self.responder = responder.Responder(driver.dns_name)

    def update(self, service_old, service_updates, responders):
        """update.

        :param service_old: previous service state
        :param service_updates: updates to service state
        :param responders: responders from providers
        :raises NotImplementedError
        """

        raise NotImplementedError

    def delete(self, provider_details):
        """delete.

        :param provider_details
        :raises NotImplementedError
        """

        raise NotImplementedError

    def create(self, responders):
        """create.

        :param responders
        :raises NotImplementedError
        """

        raise NotImplementedError

    def generate_shared_ssl_domain_suffix(self):
        """Generate a shared ssl domain suffix,

        to be used with manager for shared ssl feature

        :raises NotImplementedError
        """

        raise NotImplementedError
