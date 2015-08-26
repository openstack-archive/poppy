# Copyright (c) 2015 Rackspace, Inc.
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

from poppy.model import common


VALID_CERT_TYPES = [u'san', u'custom']


class SSLCertificate(common.DictSerializableModel):

    """SSL Certificate Class."""

    def __init__(self,
                 flavor_id,
                 domain_name,
                 cert_type,
                 cert_detail={}):
        self._flavor_id = flavor_id
        self._domain_name = domain_name
        self._cert_type = cert_type
        self._cert_detail = cert_detail

    @property
    def flavor_id(self):
        """Get or set flavor ref."""
        return self._flavor_id

    @flavor_id.setter
    def flavor_id(self, value):
        self._flavor_id = value

    @property
    def domain_name(self):
        """Get service id."""
        return self._domain_name

    @domain_name.setter
    def domain_name(self, value):
        self._domain_name = value

    @property
    def cert_type(self):
        """Get service id."""
        return self._cert_type

    @cert_type.setter
    def cert_type(self, value):
        if (value in VALID_CERT_TYPES):
            self._cert_type = value
        else:
            raise ValueError(
                u'Cert type: {0} not in valid options: {1}'.format(
                    value,
                    VALID_CERT_TYPES)
            )

    @property
    def cert_detail(self):
        """Get service id."""
        return self._cert_detail

    @cert_detail.setter
    def cert_detail(self, valueS):
        """Get service id."""
        return self._cert_type
