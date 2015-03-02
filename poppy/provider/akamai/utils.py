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
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
import ssl


from OpenSSL import crypto
import six

# Python 3 does not have ssl.PROTOCOL_SSLv2, but has PROTOCOL_TLSv1_1,
# PROTOCOL_TLSv1_2, and for some reason Jenkins will not pil up these
# new versions
try:
    if six.PY2:
        extra_versions = [ssl.PROTOCOL_SSLv2]    # pragma: no cover
    if six.PY3:                                  # pragma: no cover
        extra_versions = [ssl.PROTOCOL_TLSv1_1,  # pragma: no cover
                          ssl.PROTOCOL_TLSv1_2]  # pragma: no cover
except AttributeError:                           # pragma: no cover
    extra_versions = []                          # pragma: no cover

ssl_versions = [
    ssl.PROTOCOL_SSLv3,
    ssl.PROTOCOL_TLSv1,
    ssl.PROTOCOL_SSLv23
]

ssl_versions.extend(extra_versions)


def get_ssl_number_of_hosts(remote_host):
    '''Get number of Alternative names for a (SAN) Cert

    '''

    for ssl_version in ssl_versions:
        try:
            cert = ssl.get_server_certificate((remote_host, 443),
                                              ssl_version=ssl_version)
        except ssl.SSLError:
            # This exception
            continue

        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        sans = []
        for idx in range(0, x509.get_extension_count()):
            extension = x509.get_extension(idx)
            if extension.get_short_name() == 'subjectAltName':
                sans = [san.replace('DNS:', '') for san
                        in str(extension).split(',')]
                break

        # We can actually print all the Subject Alternative Names
        # for san in sans:
        #    print san
        result = len(sans)
        break
    else:
        raise ValueError('Get remote host certificate info failed...')
    return result


class WhoisDotComHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.find_registra_info = False
        self.registra_data = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'id' and (value == 'registrarData'
                                 or value == 'registry'):
                self.find_registra_info = True

    def handle_data(self, data):
        if self.find_registra_info:
            self.registra_data.append(data)

    def handle_endtag(self, tag):
        if self.find_registra_info:
            self.find_registra_info = False


def parseRegistraData(registra_data_list):
    result = {}
    for idx, data in enumerate(registra_data_list):
        if 'Registrant Country' in data:
            result['csr.cn'] = data.split(":")[1].strip().replace(' ', '+')
        if 'Registrant State/Province' in data:
            result['csr.st'] = data.split(":")[1].strip().replace(' ', '+')
        if 'Registrant City' in data:
            result['csr.l'] = data.split(":")[1].strip().replace(' ', '+')
        if 'Registrant Organization' in data:
            result['csr.o'] = (
                data.split(":")[1].strip().replace(' ', '+'))
        result['csr.ou'] = 'IT'
        if 'csr.o' in result:
            result['organization-information.organization-name'] = (
                result['csr.o'])
        if 'Registrant Street' in data:
            result['organization-information.address-line-one'] = (
                data.split(":")[1].strip().replace(' ', '+'))
        if 'csr.l' in result:
            result['organization-information.city'] = result['csr.l']
        if 'csr.st' in result:
            result['organization-information.region'] = result['csr.st']
        if 'csr.cn' in result:
            result['organization-information.country'] = result['csr.cn']
        if 'Registrant Postal Code' in data:
            result['organization-information.postal-code'] = (
                data.split(":")[1].strip())
        if 'Admin Name:' in data:
            admin_names = data.split(':')[1].split(' ')
            result['admin-contact.first-name'] = admin_names[0].strip()
            if len(admin_names) > 1:
                result['admin-contact.last-name'] = admin_names[1].strip()
        if "Admin Email:" in data:
            result['admin-contact.email'] = (
                registra_data_list[idx+1].replace("@", "%40"))
        if "Admin Phone:" in data:
            result['admin-contact.phone'] = (
                data.split(":")[1].strip().replace('.', ''))
        if 'Tech Name:' in data:
            tech_names = data.split(':')[1].split(' ')
            result['technical-contact.first-name'] = tech_names[0].strip()
            if len(tech_names) > 1:
                result['technical-contact.last-name'] = tech_names[1].strip()
        if "Tech Email:" in data:
            result['technical-contact.email'] = (
                registra_data_list[idx+1].replace("@", "%40"))
        if "Tech Phone:" in data:
            result['technical-contact.phone'] = (
                data.split(":")[1].strip().replace('.', ''))
    return result
