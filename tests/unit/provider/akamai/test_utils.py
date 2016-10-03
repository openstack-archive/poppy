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

import ssl

import mock

from poppy.provider.akamai import utils
from tests.unit import base


class TestAkamaiUtils(base.TestCase):

    def setUp(self):
        super(TestAkamaiUtils, self).setUp()

        ssl_server_cert_patcher = mock.patch('ssl.get_server_certificate')
        self.mock_get_server_cert = ssl_server_cert_patcher.start()
        self.addCleanup(ssl_server_cert_patcher.stop)

        ssl_crypto_patcher = mock.patch('OpenSSL.crypto.load_certificate')
        self.mock_ssl_crypto = ssl_crypto_patcher.start()
        self.addCleanup(ssl_crypto_patcher.stop)

        ssl_context_patcher = mock.patch('ssl.create_default_context')
        self.mock_ssl_context = ssl_context_patcher.start()
        self.addCleanup(ssl_context_patcher.stop)

        context_patcher = mock.patch('ssl.SSLContext')
        self.mock_context = context_patcher.start()
        self.addCleanup(context_patcher.stop)

        self.mock_ssl_context.return_value.wrap_socket.return_value. \
            getpeercert.return_value = {
                'issuer': (
                    (('countryName', 'IL'),),
                    (('organizationName', 'Issuer Ltd.'),),
                    (('organizationalUnitName', 'Secure Cert Signing'),),
                    (('commonName', 'Secure CA'),)
                ),
                'notAfter': 'Nov 22 08:15:19 2013 GMT',
                'notBefore': 'Nov 21 03:09:52 2011 GMT',
                'serialNumber': 'DEAD',
                'subject': (
                    (('description', 'Some-DESCRIPTION'),),
                    (('countryName', 'US'),),
                    (('stateOrProvinceName', 'Georgia'),),
                    (('localityName', 'Atlanta'),),
                    (('organizationName', 'R_Host, Inc.'),),
                    (('commonName', '*.r_host'),),
                    (('emailAddress', 'host_master@r_host'),)
                ),
                'subjectAltName': (('DNS', '*.r_host'), ('DNS', 'r_host')),
                'version': 3
            }

    def test_get_ssl_number_of_hosts_alternate(self):
        self.assertEqual(
            2, utils.get_ssl_number_of_hosts_alternate('remote_host'))

    def test_get_sans_by_host_alternate(self):
        self.assertEqual(
            ['*.r_host', 'r_host'],
            utils.get_sans_by_host_alternate('remote_host')
        )

    def test_get_ssl_positive(self):
        def get_cert(tuple, ssl_version):
            if ssl_version == ssl.PROTOCOL_TLSv1:
                return mock.MagicMock()
            else:
                raise ssl.SSLError()

        self.mock_get_server_cert.side_effect = get_cert

        id_mock = mock.MagicMock()
        id_mock.get_short_name.return_value = 'subjectAltName'
        id_mock.__str__.return_value = 'r_host'

        def get_ext(index):
            if index == 0:
                return id_mock
            else:
                return mock.Mock()

        self.mock_ssl_crypto.return_value.\
            get_extension_count.return_value = 2
        self.mock_ssl_crypto.return_value.\
            get_extension.side_effect = get_ext

        self.assertEqual(1, utils.get_ssl_number_of_hosts('remote_host'))
        self.assertEqual(['r_host'], utils.get_sans_by_host('remote_host'))

    def test_get_ssl_no_extensions_on_cert(self):
        def get_cert(tuple, ssl_version):
            if ssl_version == ssl.PROTOCOL_TLSv1:
                return mock.MagicMock()
            else:
                raise ssl.SSLError()

        self.mock_get_server_cert.side_effect = get_cert

        id_mock = mock.MagicMock()
        id_mock.get_short_name.return_value = 'subjectAltName'
        id_mock.__str__.return_value = 'r_host'

        def get_ext(index):
            if index == 0:
                return id_mock
            else:
                return mock.Mock()

        self.mock_ssl_crypto.return_value.\
            get_extension_count.return_value = 0
        self.mock_ssl_crypto.return_value.\
            get_extension.side_effect = get_ext

        self.assertEqual(0, utils.get_ssl_number_of_hosts('remote_host'))
        self.assertEqual([], utils.get_sans_by_host('remote_host'))

    def test_get_ssl_no_san_extension(self):
        def get_cert(tuple, ssl_version):
            if ssl_version == ssl.PROTOCOL_TLSv1:
                return mock.MagicMock()
            else:
                raise ssl.SSLError()

        self.mock_get_server_cert.side_effect = get_cert

        id_mock = mock.MagicMock()

        def get_ext(index):
            if index == 0:
                return id_mock
            else:
                return mock.Mock()

        self.mock_ssl_crypto.return_value.\
            get_extension_count.return_value = 2
        self.mock_ssl_crypto.return_value.\
            get_extension.side_effect = get_ext

        self.assertEqual(0, utils.get_ssl_number_of_hosts('remote_host'))
        self.assertEqual([], utils.get_sans_by_host('remote_host'))

    def test_get_ssl_number_of_hosts_exception(self):
        self.mock_get_server_cert.side_effect = ssl.SSLError()

        id_mock = mock.MagicMock()
        id_mock.get_short_name.return_value = 'subjectAltName'
        id_mock.__str__.return_value = 'r_host'

        def get_ext(index):
            if index == 0:
                return id_mock
            else:
                return mock.Mock()

        self.mock_ssl_crypto.return_value.\
            get_extension_count.return_value = 2
        self.mock_ssl_crypto.return_value.\
            get_extension.side_effect = get_ext

        self.assertRaises(
            ValueError, utils.get_ssl_number_of_hosts, 'remote_host')
        self.assertRaises(ValueError, utils.get_sans_by_host, 'remote_host')

    def test_default_context_error(self):
        self.mock_ssl_context.side_effect = AttributeError(
            'Mock -- Something went wrong create default context.'
        )
        self.mock_context.return_value.wrap_socket.return_value. \
            getpeercert.return_value = {
                'issuer': (
                    (('countryName', 'IL'),),
                    (('organizationName', 'Issuer Ltd.'),),
                    (('organizationalUnitName', 'Secure Cert Signing'),),
                    (('commonName', 'Secure CA'),)
                ),
                'notAfter': 'Nov 22 08:15:19 2013 GMT',
                'notBefore': 'Nov 21 03:09:52 2011 GMT',
                'serialNumber': 'DEAD',
                'subject': (
                    (('description', 'Some-DESCRIPTION'),),
                    (('countryName', 'US'),),
                    (('stateOrProvinceName', 'Georgia'),),
                    (('localityName', 'Atlanta'),),
                    (('organizationName', 'R_Host, Inc.'),),
                    (('commonName', '*.r_host'),),
                    (('emailAddress', 'host_master@r_host'),)
                ),
                'subjectAltName': (('DNS', '*.r_host'), ('DNS', 'r_host')),
                'version': 3
            }

        self.assertEqual(
            2, utils.get_ssl_number_of_hosts_alternate('remote_host'))
