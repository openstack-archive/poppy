# Copyright (c) 2016 Rackspace, Inc.
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
class CertificatesControllerBase(controller.StorageControllerBase):

    @abc.abstractmethod
    def create_certificate(self, project_id, cert_obj):
        """Create a certificate

        :param project_id
        :param cert_obj
        :raise NotImplementedError
        """
        raise NotImplementedError

    def delete_certificate(self, project_id, domain_name, cert_type):
        """Delete a certificate.

        :param project_id
        :param domain_name
        :param cert_type
        :raise NotImplementedError
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_certificate(self, domain_name, cert_type, flavor_id,
                           cert_details):
        """update_cert_info.

        :param domain_name
        :param cert_type
        :param flavor_id
        :param cert_details
        """
        raise NotImplementedError
