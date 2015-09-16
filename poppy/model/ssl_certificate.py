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
VALID_STATUS_IN_CERT_DETAIL = [
    u'deployed',
    u'create_in_progress',
    u'failed'
]


class SSLCertificate(common.DictSerializableModel):

    """SSL Certificate Class."""

    def __init__(self,
                 flavor_id,
                 domain_name,
                 cert_type,
                 cert_details={}):
        self._flavor_id = flavor_id
        self._domain_name = domain_name
        self._cert_type = cert_type
        self._cert_details = cert_details

    @property
    def flavor_id(self):
        """Get or set flavor ref."""
        return self._flavor_id

    @flavor_id.setter
    def flavor_id(self, value):
        self._flavor_id = value

    @property
    def domain_name(self):
        """Get domain name"""
        return self._domain_name

    @domain_name.setter
    def domain_name(self, value):
        self._domain_name = value

    @property
    def cert_type(self):
        """Get cert type."""
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
    def cert_details(self):
        """Get cert_details."""
        return self._cert_details

    @cert_details.setter
    def cert_details(self, value):
        """Set cert details."""
        self._cert_type = value

    def get_cert_status(self):
        if self.cert_details is None or self.cert_details == {}:
            return "deployed"
        # Note(tonytan4ever): Right now we assume there is only one
        # provider per flavor (that is akamai), so the first one
        # value of this dictionary is akamai cert_details
        first_provider_cert_details = (
            self.cert_details.values()[0].get("extra_info", None))
        if first_provider_cert_details is None:
            return "deployed"
        else:
            result = first_provider_cert_details.get('status', "deployed")
            if result not in VALID_STATUS_IN_CERT_DETAIL:
                raise ValueError(
                    u'Status in cert_details: {0} not in valid options: {1}'.
                    format(
                        result,
                        VALID_STATUS_IN_CERT_DETAIL
                    )
                )
            return result

    def get_san_edge_name(self):
        if self.cert_type == 'san':
            if self.cert_details is None or self.cert_details == {}:
                return None
            first_provider_cert_details = (
                self.cert_details.values()[0].get("extra_info", None))
            if first_provider_cert_details is None:
                return None
            else:
                return first_provider_cert_details.get('san cert', None)
        else:
            return None
