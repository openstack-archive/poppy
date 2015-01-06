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


class Rule(common.DictSerializableModel):
    """Rule."""

    def __init__(self, name,
                 referrer=None, http_host=None, client_ip=None,
                 http_method=None, request_url=None):
        self._name = name
        self._referrer = referrer
        self._http_host = http_host
        self._client_ip = client_ip
        self._http_method = http_method
        self._request_url = request_url

    @property
    def name(self):
        """name."""
        return self._name

    @property
    def referrer(self):
        return self._referrer

    @referrer.setter
    def referrer(self, value):
        self._referrer = value

    @property
    def http_host(self):
        """http_host."""
        return self._http_host

    @http_host.setter
    def http_host(self, value):
        self._http_host = value

    @property
    def client_ip(self):
        return self._client_ip

    @client_ip.setter
    def client_ip(self, value):
        self._client_ip = value

    @property
    def http_method(self):
        return self._http_method

    @http_method.setter
    def http_method(self, value):
        self._http_method = value

    @property
    def request_url(self):
        return self._request_url

    @request_url.setter
    def request_url(self, value):
        self._request_url = value

    def to_dict(self):
        result = common.DictSerializableModel.to_dict(self)

        result['name'] = self._name
        result['referrer'] = self._referrer
        result['http_host'] = self._http_host
        result['client_ip'] = self._client_ip
        result['http_method'] = self._http_method
        result['request_url'] = self._request_url

        return result