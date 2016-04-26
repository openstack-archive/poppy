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

import random

from poppy.model import ssl_certificate
from poppy.storage import base


class CertificatesController(base.CertificatesController):

    def __init__(self, driver):
        super(CertificatesController, self).__init__(driver)

        self.certs = {}

    def create_certificate(self, project_id, cert_obj):
        key = (cert_obj.flavor_id, cert_obj.domain_name, cert_obj.cert_type)
        if key not in self.certs:
            self.certs[key] = cert_obj
        else:
            raise ValueError

    def delete_certificate(self, project_id, domain_name, cert_type):
        if "non_exist" in domain_name:
            raise ValueError("No certs on this domain")

    def update_certificate(self, domain_name, cert_type, flavor_id,
                           cert_details):
        key = (flavor_id, domain_name, cert_type)
        if key in self.certs:
            self.certs[key].cert_details = cert_details

    def get_certs_by_domain(self, domain_name, project_id=None,
                            flavor_id=None,
                            cert_type=None,
                            status=u'create_in_progress'):
        certs = []
        for cert in self.certs:
            if domain_name in cert:
                certs.append(self.certs[cert])
        if project_id:
            if flavor_id is not None and cert_type is not None:
                return ssl_certificate.SSLCertificate(
                    "premium",
                    "blog.testabcd.com",
                    "san",
                    project_id=project_id,
                    cert_details={
                        'Akamai': {
                            u'cert_domain': u'secure2.san1.test_123.com',
                            u'extra_info': {
                                u'action': u'Waiting for customer domain '
                                           'validation for blog.testabc.com',
                                u'akamai_spsId': str(random.randint(1, 100000)
                                                     ),
                                u'create_at': u'2015-09-29 16:09:12.429147',
                                u'san cert': u'secure2.san1.test_123.com',
                                u'status': status}
                        }
                    }
                )
            return [cert for cert in certs if cert.project_id == project_id]
        else:
            return certs
