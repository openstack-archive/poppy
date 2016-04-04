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

from poppy.provider.base import controller
from poppy.provider.base import responder


@six.add_metaclass(abc.ABCMeta)
class CertificatesControllerBase(controller.ProviderControllerBase):
    """Services Controller Base."""

    def __init__(self, driver):
        super(CertificatesControllerBase, self).__init__(driver)

        self.responder = responder.Responder(driver.provider_name)

    @abc.abstractmethod
    def create_certificate(self, cert_obj, enqueue=True):
        """Create a certificate.

        :param cert_obj
        :param enqueue
        :raises NotImplementedError
        """
        raise NotImplementedError
