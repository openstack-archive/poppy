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

import json
import os

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

SAN_CERT_RECORDS_FILE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))),
    'provider', 'akamai',
    'SAN_certs.data')


SAN_CERT_DATA_TEMPALTE = {
    'cnameHostname': '{{hostname}}',
    'issuer': 'symantec',
    'createType': 'san',
    'csr.cn': '{{crs.cn}}',
    'csr.c': '{{csr.c}}',
    'csr.st': '{{csr.st}}',
    'csr.l': '{{csr.l}}',
    'csr.o': '{{csr.o}}',
    'csr.ou': '{{csr.ou}}',
    'csr.sans': '{{hostname}}',
    'organization-information.organization-name': '{{organization}}',
    'organization-information.address-line-one':  '{{organization'
    '-address-line-one}}',
    'organization-information.city': '{{organization-city}}',
    'organization-information.region': '{{organization-tx}}',
    'organization-information.postal-code': '{{organization-postal-code}}',
    'organization-information.country': '{{organization-country}}',
    'organization-information.phone': '{{organization-phone}}',
    'admin-contact.first-name': '{{admin-first-name}}',
    'admin-contact.last-name': '{{admin-last-name}}',
    'admin-contact.phone': '{{admin-contact}}',
    # needs to url encode the email id
    # example:zali%40akamai.com
    'admin-contact.email': '{{admin-contact-email}}',
    'technical-contact.first-name': '{{technical-first-name}}',
    'technical-contact.last-name': '{{technical-last-name}}',
    'technical-contact.phone': '{{technical-contact-phone}}',
    'technical-contact.email': '{{technical-contact-email}}',
    'ipVersion': 'ipv4',
    ##################
    # 'product' : 'alta',
    'slot-deployment.klass': 'esslType'
}


class CreateSANCertTask(task.Task):
    default_provides = 'spsId'

    def __init__(self):
        super(CreateSANCertTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj

    def execute(self, san_cert_creation_info_dict):
        data = self.get_san_cert_creation_data(san_cert_creation_info_dict)
        cnameHostName = data['csr.cn']
        # Mannually concatenate all input data string
        s_data = '&'.join(['%s=%s' % (k, v) for (k, v) in data.items()])
        resp = self.akamai_driver.akamai_sps_api_client.post(
            self.akamai_driver.akamai_sps_api_base_url.format(spsId=""),
            data=s_data
        )
        if resp.status_code != 202:
            raise RuntimeError('SPS Request failed.'
                               'Exception: %s' % resp.text)

        resp_data = json.loads(resp.text)
        spsId = resp_data['spsId']
        jobID = resp_data['Results']['data'][0]['results']['jobID']

        message = {
            'spsId': spsId,
            'jobID': jobID,
            'cnameHostname': cnameHostName
        }

        self.sc.enqueue_status_check_queue(
            {'SPSStatusCheck': spsId},
            [json.dumps([
                'secureEdgeHost',
                message])])

        return spsId

    def get_san_cert_creation_data(self, san_cert_creation_info_dict):
        """Takes in a dictionory to fill in SAN_CERT_DATA_TEMPALTE info

        """
        SAN_CERT_DATA_TEMPALTE['cnameHostname'] = (
            san_cert_creation_info_dict.get('cnamehostname', ''))

        SAN_CERT_DATA_TEMPALTE['csr.cn'] = (
            san_cert_creation_info_dict.get('csr.cn', ''))
        SAN_CERT_DATA_TEMPALTE['csr.c'] = (
            san_cert_creation_info_dict.get('csr.c', ''))
        SAN_CERT_DATA_TEMPALTE['csr.st'] = (
            san_cert_creation_info_dict.get('csr.st', ''))
        SAN_CERT_DATA_TEMPALTE['csr.l'] = (
            san_cert_creation_info_dict.get('csr.l', ''))
        SAN_CERT_DATA_TEMPALTE['csr.o'] = (
            san_cert_creation_info_dict.get('csr.o', ''))
        SAN_CERT_DATA_TEMPALTE['csr.ou'] = (
            san_cert_creation_info_dict.get('csr.ou', ''))
        SAN_CERT_DATA_TEMPALTE['csr.sans'] = (
            san_cert_creation_info_dict.get('csr.sans', ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.'
                               'organization-name'] = (
            san_cert_creation_info_dict.get('organization-information.'
                                            'organization-name', ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.address-line-one'] = (
            san_cert_creation_info_dict.get('organization-information.'
                                            'address-line-one', ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.city'] = (
            san_cert_creation_info_dict.get('organization-information.city',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.region'] = (
            san_cert_creation_info_dict.get('organization-information.region',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.postal-code'] = (
            san_cert_creation_info_dict.get('organization-information.'
                                            'postal-code', ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.country'] = (
            san_cert_creation_info_dict.get('organization-information.country',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['organization-information.phone'] = (
            san_cert_creation_info_dict.get('organization-information.phone',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['admin-contact.first-name'] = (
            san_cert_creation_info_dict.get('admin-contact.first-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['admin-contact.last-name'] = (
            san_cert_creation_info_dict.get('admin-contact.last-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['admin-contact.phone'] = (
            san_cert_creation_info_dict.get('admin-contact.phone',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['admin-contact.email'] = (
            san_cert_creation_info_dict.get('admin-contact.email',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['technical-contact.first-name'] = (
            san_cert_creation_info_dict.get('technical-contact.first-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['technical-contact.last-name'] = (
            san_cert_creation_info_dict.get('technical-contact.last-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['technical-contact.phone'] = (
            san_cert_creation_info_dict.get('technical-contact.last-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['technical-contact.email'] = (
            san_cert_creation_info_dict.get('technical-contact.last-name',
                                            ''))
        SAN_CERT_DATA_TEMPALTE['technical-contact.last-name'] = (
            san_cert_creation_info_dict.get('technical-contact.last-name',
                                            ''))

        return SAN_CERT_DATA_TEMPALTE
