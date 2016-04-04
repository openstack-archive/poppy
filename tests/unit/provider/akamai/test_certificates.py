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

import ddt
import mock

from poppy.provider.akamai import certificates
from poppy.transport.pecan.models.request import ssl_certificate
from tests.unit import base


@ddt.ddt
class TestCertificates(base.TestCase):

    def setUp(self):
        super(TestCertificates, self).setUp()
        self.driver = mock.Mock()
        self.san_cert_cnames = [str(x) for x in range(7)]
        self.driver.san_cert_cnames = self.san_cert_cnames

        self.controller = certificates.CertificateController(self.driver)

    @ddt.data(("SPS Request Complete", ""),
              ("edge host already created or pending", None),
              ("CPS cancelled", None),
              ("edge host already created or pending", "Some progress info"))
    def test_create_ssl_certificate_happy_path(
            self,
            sps_status_and_workflow_progress):
        sps_status, work_flow_progress = sps_status_and_workflow_progress
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com",
                                       "secure.san2.poppycdn.com"]

        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        last_sps_id = (
            self.controller.san_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        self.controller.san_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        cert_info = self.controller.san_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"
        string_post_cert_info = '&'.join(
            ['%s=%s' % (k, v) for (k, v) in cert_info.items()])

        self.controller.sps_api_client.get.return_value = mock.Mock(
            status_code=200,
            # Mock an SPS request
            text=json.dumps({
                "requestList":
                    [{"resourceUrl": "/config-secure-provisioning-service/"
                                     "v1/sps-requests/1849",
                        "parameters": [{
                            "name": "cnameHostname",
                            "value": "secure.san1.poppycdn.com"
                            }, {"name": "createType", "value": "modSan"},
                            {"name": "csr.cn",
                             "value": "secure.san3.poppycdn.com"},
                            {"name": "add.sans",
                             "value": "www.abc.com"}],
                     "lastStatusChange": "2015-03-19T21:47:10Z",
                        "spsId": 1789,
                        "status": sps_status,
                        "workflowProgress": work_flow_progress,
                        "jobId": 44306}]})
        )
        self.controller.sps_api_client.post.return_value = mock.Mock(
            status_code=202,
            text=json.dumps({
                "spsId": 1789,
                "resourceLocation":
                    "/config-secure-provisioning-service/v1/sps-requests/1856",
                "Results": {
                    "size": 1,
                    "data": [{
                        "text": None,
                        "results": {
                            "type": "SUCCESS",
                            "jobID": 44434}
                    }]}})
        )

        self.controller.create(ssl_certificate.load_from_json(data), False)

        self.controller.sps_api_client.get.assert_called_once_with(
            self.controller.sps_api_base_url.format(spsId=last_sps_id))
        self.controller.sps_api_client.post.assert_called_once_with(
            self.controller.sps_api_base_url.format(spsId=last_sps_id),
            data=string_post_cert_info.encode('utf-8'))
        return

    @ddt.data(("CPS running", ""),
              ("edge host already created or pending", "Error in it"))
    def test_create_ssl_certificate_negative_path(
            self,
            sps_status_and_work_flow_progress):
        sps_status, work_flow_progress = sps_status_and_work_flow_progress
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com"]

        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        last_sps_id = (
            self.controller.san_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        self.controller.san_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        cert_info = self.controller.san_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"

        self.controller.sps_api_client.get.return_value = mock.Mock(
            status_code=200,
            # Mock an SPS request
            text=json.dumps({
                "requestList":
                    [{"resourceUrl": "/config-secure-provisioning-service/"
                                     "v1/sps-requests/1849",
                        "parameters": [{
                            "name": "cnameHostname",
                            "value": "secure.san1.poppycdn.com"
                            }, {"name": "createType", "value": "modSan"},
                            {"name": "csr.cn",
                             "value": "secure.san3.poppycdn.com"},
                            {"name": "add.sans",
                             "value": "www.abc.com"}],
                     "lastStatusChange": "2015-03-19T21:47:10Z",
                        "spsId": 1789,
                        "status": sps_status,
                        "workFlowProgress": work_flow_progress,
                        "jobId": 44306}]})
        )
        self.controller.sps_api_client.post.return_value = mock.Mock(
            status_code=202,
            text=json.dumps({
                "spsId": 1789,
                "resourceLocation":
                    "/config-secure-provisioning-service/v1/sps-requests/1856",
                "Results": {
                    "size": 1,
                    "data": [{
                        "text": None,
                        "results": {
                            "type": "SUCCESS",
                            "jobID": 44434}
                    }]}})
        )
        self.controller.create(
            ssl_certificate.load_from_json(data),
            False)
        self.controller.sps_api_client.get.assert_called_once_with(
            self.controller.sps_api_base_url.format(spsId=last_sps_id))
        self.assertFalse(self.controller.sps_api_client.post.called)
