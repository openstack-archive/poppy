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

import uuid

import ddt
from hypothesis import given
from hypothesis import strategies
import mock
import six

from poppy.manager.default.services import DefaultServicesController

from tests.functional.transport.pecan import base


@ddt.ddt
class TestGetDomainsbyProviderurl(base.FunctionalTest):

    def test_get_domains_provider_url_no_queryparam(self):
        # no provider_url field
        url = '/v1.0/admin/domains'
        response = self.app.get(url,
                                headers={'Content-Type':
                                         'application/json',
                                         'X-Project-ID':
                                         str(uuid.uuid4())},
                                expect_errors=True)
        self.assertEqual(response.status_code, 400)

    @given(strategies.text())
    def test_get_domains_provider_url_invalid_queryparam(self,
                                                         provider_url):
        # invalid provider_url field
        try:
            # NOTE(TheSriram): Py3k Hack
            if six.PY3 and type(provider_url) == str:
                provider_url = provider_url.encode('utf-8')
                url = '/v1.0/admin/domains?' \
                      'provider_url={0}'.format(provider_url)

            else:
                url = '/v1.0/admin/domains?provider_url=%s' \
                      % provider_url.decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        else:
            response = self.app.get(url,
                                    headers={'Content-Type':
                                             'application/json',
                                             'X-Project-ID':
                                             str(uuid.uuid4())},
                                    expect_errors=True)

            self.assertEqual(response.status_code, 400)

    @ddt.data('provider.com.extension.provideredge.net',
              'secure.shard.domain.com.provideredge.net',
              'www.domain.com.provideredge.net')
    def test_get_domains_provider_url_valid_queryparam(self, provider_url):
        # valid provider_url
        with mock.patch.object(DefaultServicesController,
                               'get_domains_by_provider_url'):
            response = self.app.get('/v1.0/admin/domains'
                                    '?provider_url={0}'.format(provider_url),
                                    headers={'Content-Type':
                                             'application/json',
                                             'X-Project-ID':
                                             str(uuid.uuid4())})

            self.assertEqual(response.status_code, 200)
