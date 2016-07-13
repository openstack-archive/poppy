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

from poppy.common import util
from poppy.model import common
from poppy.model.helpers import geo_zones


class Rule(common.DictSerializableModel):
    """Rule."""

    def __init__(self, name=None,
                 referrer=None, http_host=None, client_ip=None,
                 geography=None, http_method=None, request_url="/*"):
        self._name = name
        self._request_url = request_url

        if referrer:
            self._referrer = referrer.strip()
        if http_host:
            self._http_host = http_host.strip()
        if client_ip:
            self._client_ip = client_ip.strip()
        if http_method:
            self._http_method = http_method.strip()
        if geography:
            # Validate the geography should be in a list of supported
            # countries
            if geography is not None and \
                geography not in geo_zones.GEO_COUNTRY_ZONES and \
                    geography not in geo_zones.GEO_REGION_ZONES:
                raise ValueError(util.help_escape(
                                 'Country/Area %s is not supported in '
                                 'geo zones' % geography))
            self._geography = geography
        if request_url:
            self._request_url = request_url.strip()

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

    @property
    def geography(self):
        """http_host."""
        return self._geography

    @geography.setter
    def geography(self, value):
        if value is not None and \
            value not in geo_zones.GEO_COUNTRY_ZONES and \
                value not in geo_zones.GEO_REGION_ZONES:
                raise ValueError(util.help_escape(
                                 'Country/Area %s is not supported in '
                                 'geo zones' % value))

        self._geography = value
