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

from poppy.model.helpers import domain
from poppy.model import ssl_certificate


def load_from_json(json_data):
    domain_name = json_data.get('domain')
    protocol = json_data.get('protocol', 'http')
    certification_option = json_data.get('certificate', None)
    res_d = domain.Domain(domain_name, protocol, certification_option)
    # Note(tonytan4ever):
    # if the domain is in binding status, set the cert_info object
    if json_data.get('cert_info') is not None:
        cert_info = ssl_certificate.SSLCertificate(
            json_data.get('cert_info').get('flavor_id'),
            domain_name,
            json_data.get('cert_info').get('cert_type'),
            json_data.get('cert_info').get('project_id'),
            json_data.get('cert_info').get('cert_details', {})
        )
        setattr(res_d, 'cert_info', cert_info)
    return res_d
