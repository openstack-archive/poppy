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

from poppy.model import common

VALID_STATUSES = [
    u'deploy_in_progress',
    u'deployed',
    u'update_in_progress',
    u'delete_in_progress',
    u'failed']


class ProviderDetail(common.DictSerializableModel):

    """ProviderDetail object for each provider."""

    def __init__(self, provider_service_id=None, access_urls={},
                 status=u"deploy_in_progress", name=None, error_info=None,
                 error_message=None):
        self._provider_service_id = provider_service_id
        self._id = provider_service_id
        self._access_urls = access_urls
        self._status = status
        self._name = name
        self._error_info = error_info
        self._error_message = error_message

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
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        self._error_message = value
