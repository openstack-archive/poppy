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


VALID_CERT_TYPES = [u'san', u'custom', u'dedicated']
VALID_STATUS_IN_CERT_DETAIL = [
    u'deployed',
    u'create_in_progress',
    u'failed',
    u'cancelled'
]


class SSLCertificate(common.DictSerializableModel):

    """SSL Certificate Class."""

    def __init__(self,
                 flavor_id,
                 domain_name,
                 cert_type,
                 project_id=None,
                 cert_details=None):
        self.flavor_id = flavor_id
        self.domain_name = domain_name
        self.cert_type = cert_type
        self.cert_details = cert_details
        self.project_id = project_id

    @property
    def flavor_id(self):
        """Get or set flavor ref."""
        return self._flavor_id

    @flavor_id.setter
    def flavor_id(self, value):
        self._flavor_id = value

    @property
    def project_id(self):
        """Get project id."""
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value

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
        if value is None:
            self._cert_details = {}
        else:
            self._cert_details = value

    def get_cert_status(self):
        if self.cert_details == {}:
            return "create_in_progress"
        # Note(tonytan4ever): Right now we assume there is only one
        # provider per flavor (that is akamai), so the first one
        # value of this dictionary is akamai cert_details
        first_provider_cert_details = (
            list(self.cert_details.values())[0].get("extra_info", None))
        if first_provider_cert_details is None:
            return "create_in_progress"
        else:
            result = first_provider_cert_details.get(
                'status', "create_in_progress")
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
                list(self.cert_details.values())[0].get("extra_info", None))
            if first_provider_cert_details is None:
                return None
            else:
                return first_provider_cert_details.get('san cert', None)
        else:
            return None

    @classmethod
    def init_from_dict(cls, input_dict):
        flavor_id = input_dict.get('flavor_id', None)
        domain_name = input_dict.get('domain_name', None)
        cert_type = input_dict.get('cert_type', None)
        cert_details = input_dict.get('cert_details', {})
        project_id = input_dict.get('project_id', None)

        ssl_cert = cls(flavor_id=flavor_id,
                       domain_name=domain_name,
                       cert_type=cert_type,
                       cert_details=cert_details,
                       project_id=project_id)

        return ssl_cert
