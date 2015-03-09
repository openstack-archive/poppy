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

from HTMLParser import HTMLParser


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
