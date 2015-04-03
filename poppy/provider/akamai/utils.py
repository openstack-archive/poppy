# Copyright (c) 2013 Rackspace, Inc.
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
import sys

import M2Crypto


ssl_versions = [
    ssl.PROTOCOL_SSLv3,
    ssl.PROTOCOL_TLSv1,
    ssl.PROTOCOL_SSLv2,
    ssl.PROTOCOL_SSLv23
]


def get_ssl_number_of_hosts(remote_host):
    '''Get number of Alternative names for a (SAN) Cert

    '''

    for ssl_version in ssl_versions:
        try:
            cert = ssl.get_server_certificate((remote_host, 443),
                                              ssl_version=ssl_version)
        except ssl.SSLError:
            # This exception m
            continue

        x509 = M2Crypto.X509.load_cert_string(cert)

        sans = x509.get_ext('subjectAltName').get_value()
        sans = sans.replace('DNS:', '').split(', ')
        # This will print the actual Alternative Names
        # for name in sans.split(', '):
        #    print(name)
        result = len(sans)
        break
    else:
        raise ValueError('Get remote host certificate info failed...')
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: %s <remote_host_you_want_get_cert_on>' % sys.argv[0])
        sys.exit(0)
    print("There are %s DNS names for SAN Cert on %s" % (
        get_ssl_number_of_hosts(sys.argv[1]), sys.argv[1]))
