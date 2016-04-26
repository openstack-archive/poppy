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

from poppy.manager.default.ssl_certificate import \
    DefaultSSLCertificateController

from tests.functional.transport.pecan import base


@ddt.ddt
class SSLCertificatebyStatusTest(base.FunctionalTest):

    @given(strategies.text())
    def test_get_certificate_status_invalid_queryparam(self, status):
        # invalid status field
        try:
            # NOTE(TheSriram): Py3k Hack
            if six.PY3 and type(status) == str:
                status = status.encode('utf-8')
                url = '/v1.0/admin/certificates?status={0}'.format(status)

            else:
                url = '/v1.0/admin/certificates?status=%s' \
                      % status.decode('utf-8')
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

    @ddt.data(u'create_in_progress', u'deployed', u'failed', u'cancelled')
    def test_get_service_status_valid_queryparam(self, status):
        # valid status
        with mock.patch.object(DefaultSSLCertificateController,
                               'get_certs_by_status'):
            response = self.app.get('/v1.0/admin/certificates'
                                    '?status={0}'.format(status),
                                    headers={'Content-Type':
                                             'application/json',
                                             'X-Project-ID':
                                             str(uuid.uuid4())})

            self.assertEqual(response.status_code, 200)
