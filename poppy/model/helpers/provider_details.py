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

try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

from poppy.model import common

VALID_STATUSES = [
    u'deploy_in_progress',
    u'deployed',
    u'update_in_progress',
    u'delete_in_progress',
    u'failed']

VALID_DOMAIN_CERTIFICATE_STATUSES = [
    u'create_in_progress',
    u'deployed',
    u'failed',
    u'cancelled']


class DomainCertificatesStatus(common.DictSerializableModel):

    def __init__(self, init_domain_statuses_value={}):
        self._domain_status_dict = init_domain_statuses_value

    def set_domain_certificate_status(self, domain, status):
        """changes one domain's status"""
        if status not in VALID_DOMAIN_CERTIFICATE_STATUSES:
            raise ValueError(
                u'Status {0} not in valid options: {1} for domain'' status'.
                format(status, VALID_DOMAIN_CERTIFICATE_STATUSES)
            )

        prev_status = self._domain_status_dict
        prev_status[domain] = status
        self._domain_status_dict = prev_status

    def get_domain_certificate_status(self, domain):
        return self._domain_status_dict.get(domain, "deployed")

    def to_dict(self):
        return self._domain_status_dict


class ProviderDetail(common.DictSerializableModel):

    """ProviderDetail object for each provider."""

    def __init__(self, provider_service_id=None, access_urls=[],
                 status=u"deploy_in_progress", name=None, error_info=None,
                 domains_certificate_status={},
                 error_message=None, error_class=None):
        self._provider_service_id = provider_service_id
        self._access_urls = access_urls
        self._status = status
        self._name = name
        self._error_info = error_info
        self._error_message = error_message
        self._error_class = error_class

        # Note(tonytan4ever): domains status is a dictionary recording each
        # domain's certificate status
        self._domains_certificate_status = DomainCertificatesStatus(
            domains_certificate_status)

    @property
    def provider_service_id(self):
        """provider_service_id."""
        return self._provider_service_id

    @provider_service_id.setter
    def provider_service_id(self, value):
        self._provider_service_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def access_urls(self):
        return self._access_urls

    @access_urls.setter
    def access_urls(self, value):
        self._access_urls = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if (value in VALID_STATUSES):
            self._status = value
        else:
            raise ValueError(
                u'Status {0} not in valid options: {1}'.format(
                    value,
                    VALID_STATUSES)
            )

    @property
    def error_info(self):
        return self._error_info

    @error_info.setter
    def error_info(self, value):
        self._error_info = value

    @property
    def domains_certificate_status(self):
        return self._domains_certificate_status

    @domains_certificate_status.setter
    def domains_certificate_status(self, value):
        self._domains_certificate_status = DomainCertificatesStatus(value)

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        self._error_message = value

    @property
    def error_class(self):
        return self._error_class

    @error_class.setter
    def error_class(self, value):
        self._error_class = value

    def get_domain_access_url(self, domain):
        '''Find an access url of a domain.

        :param domain
        '''
        for access_url in self.access_urls:
            if access_url.get('domain') == domain:
                return access_url
        return None

    def to_dict(self):
        result = collections.OrderedDict()
        result["id"] = self.provider_service_id
        result["access_urls"] = self.access_urls
        result["status"] = self.status
        result["name"] = self.name
        result["domains_certificate_status"] = (
            self.domains_certificate_status.to_dict())
        result["error_info"] = self.error_info
        result["error_message"] = self.error_message
        result["error_class"] = self.error_class
        return result

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """

        o = cls("unnamed")
        o.provider_service_id = dict_obj.get("id",
                                             "unknown_id")
        o.access_urls = dict_obj.get("access_urls", [])
        o.status = dict_obj.get("status", u"deploy_in_progress")
        o.domains_certificate_status = dict_obj.get(
            "domains_certificate_status", {})
        o.name = dict_obj.get("name", None)
        o.error_info = dict_obj.get("error_info", None)
        o.error_message = dict_obj.get("error_message", None)
        o.error_class = dict_obj.get("error_class", None)
        return o
