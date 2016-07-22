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
        self.driver.provider_name = 'Akamai'
        self.san_cert_cnames = [str(x) for x in range(7)]
        self.driver.san_cert_cnames = self.san_cert_cnames
        self.driver.akamai_https_access_url_suffix = (
            'example.net'
        )

        san_by_host_patcher = mock.patch(
            'poppy.provider.akamai.utils.get_sans_by_host'
        )
        self.mock_get_sans_by_host = san_by_host_patcher.start()
        self.addCleanup(san_by_host_patcher.stop)

        ssl_number_of_hosts_patcher = mock.patch(
            'poppy.provider.akamai.utils.get_ssl_number_of_hosts'
        )
        self.mock_get_ssl_number_of_hosts = ssl_number_of_hosts_patcher.start()
        self.addCleanup(ssl_number_of_hosts_patcher.stop)

        self.mock_get_sans_by_host.return_value = []
        self.mock_get_ssl_number_of_hosts.return_value = 10

        self.controller = certificates.CertificateController(self.driver)

    @ddt.data(("SPS Request Complete", ""),
              ("edge host already created or pending", None),
              ("CPS cancelled", None),
              ("edge host already created or pending", "Some progress info"))
    def test_create_ssl_certificate_happy_path(
            self,
            sps_status_workFlowProgress_tuple):
        sps_status, workFlowProgress = sps_status_workFlowProgress_tuple
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com",
                                       "secure.san2.poppycdn.com"]

        controller = certificates.CertificateController(self.driver)
        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        lastSpsId = (
            controller.cert_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        controller.cert_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        controller.cert_info_storage.get_san_cert_hostname_limit. \
            return_value = 80

        cert_info = controller.cert_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"
        string_post_cert_info = '&'.join(
            ['%s=%s' % (k, v) for (k, v) in cert_info.items()])

        controller.sps_api_client.get.return_value = mock.Mock(
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
                      "workflowProgress": workFlowProgress,
                      "jobId": 44306}]})
        )
        controller.sps_api_client.post.return_value = mock.Mock(
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
        controller.create_certificate(
            ssl_certificate.load_from_json(data),
            False
        )
        controller.sps_api_client.get.assert_called_once_with(
            controller.sps_api_base_url.format(spsId=lastSpsId))
        controller.sps_api_client.post.assert_called_once_with(
            controller.sps_api_base_url.format(spsId=lastSpsId),
            data=string_post_cert_info.encode('utf-8'))
        return

    @ddt.data(("CPS running", ""),
              ("edge host already created or pending", "Error in it"))
    def test_create_ssl_certificate_negative_path(
            self,
            sps_status_workFlowProgress_tuple):
        sps_status, workFlowProgress = sps_status_workFlowProgress_tuple
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com"]

        controller = certificates.CertificateController(self.driver)
        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        lastSpsId = (
            controller.cert_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        controller.cert_info_storage.get_san_cert_hostname_limit. \
            return_value = 80

        controller.cert_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        cert_info = controller.cert_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"

        controller.sps_api_client.get.return_value = mock.Mock(
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
                      "workflowProgress": workFlowProgress,
                      "jobId": 44306}]})
        )
        controller.sps_api_client.post.return_value = mock.Mock(
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
        controller.create_certificate(ssl_certificate.load_from_json(data),
                                      False)
        controller.sps_api_client.get.assert_called_once_with(
            controller.sps_api_base_url.format(spsId=lastSpsId))
        self.assertFalse(controller.sps_api_client.post.called)
        return

    def test_create_ssl_certificate_cert_type_not_implemented(self):
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com",
                                       "secure.san2.poppycdn.com"]

        controller = certificates.CertificateController(self.driver)

        ssl_cert = mock.Mock()
        type(ssl_cert).cert_type = mock.PropertyMock(
            return_value='unsupported-type'
        )

        responder = controller.create_certificate(
            ssl_cert,
            False
        )

        self.assertIsNone(responder['Akamai']['cert_domain'])
        self.assertEqual(
            'failed',
            responder['Akamai']['extra_info']['status']
        )
        self.assertEqual(
            "Cert type : unsupported-type hasn't been implemented",
            responder['Akamai']['extra_info']['reason']
        )

    def test_create_ssl_certificate_sps_api_get_failure(self):
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com",
                                       "secure.san2.poppycdn.com"]

        controller = certificates.CertificateController(self.driver)
        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        lastSpsId = (
            controller.cert_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        controller.cert_info_storage.get_san_cert_hostname_limit. \
            return_value = 80

        controller.cert_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        cert_info = controller.cert_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"

        controller.sps_api_client.get.return_value = mock.Mock(
            status_code=404,
            # Mock an SPS request
            text='SPS ID NOT FOUND'
        )

        responder = controller.create_certificate(
            ssl_certificate.load_from_json(data),
            False
        )

        controller.sps_api_client.get.assert_called_once_with(
            controller.sps_api_base_url.format(spsId=lastSpsId))

        self.assertIsNone(responder['Akamai']['cert_domain'])
        self.assertEqual(
            'create_in_progress',
            responder['Akamai']['extra_info']['status']
        )
        self.assertEqual(
            'San cert request for www.abc.com has been enqueued.',
            responder['Akamai']['extra_info']['action']
        )
        mod_san_q = self.driver.mod_san_queue

        mod_san_q.enqueue_mod_san_request.assert_called_once_with(
            json.dumps(ssl_certificate.load_from_json(data).to_dict())
        )

    def test_create_ssl_certificate_sps_api_post_failure(self):
        self.driver.san_cert_cnames = ["secure.san1.poppycdn.com",
                                       "secure.san2.poppycdn.com"]

        controller = certificates.CertificateController(self.driver)
        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        lastSpsId = (
            controller.cert_info_storage.get_cert_last_spsid(
                "secure.san1.poppycdn.com"))

        controller.cert_info_storage.get_san_cert_hostname_limit. \
            return_value = 80

        controller.cert_info_storage.get_cert_info.return_value = {
            'cnameHostname': "secure.san1.poppycdn.com",
            'jobId': "secure.san1.poppycdn.com",
            'issuer': 1789,
            'createType': 'modSan',
            'ipVersion': 'ipv4',
            'slot-deployment.class': 'esslType'
        }

        cert_info = controller.cert_info_storage.get_cert_info(
            "secure.san1.poppycdn.com")
        cert_info['add.sans'] = "www.abc.com"

        controller.sps_api_client.get.return_value = mock.Mock(
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
                      "status": "SPS Request Complete",
                      "workflowProgress": "",
                      "jobId": 44306}]})
        )

        controller.sps_api_client.post.return_value = mock.Mock(
            status_code=500,
            text='INTERNAL SERVER ERROR'
        )

        responder = controller.create_certificate(
            ssl_certificate.load_from_json(data),
            False
        )

        controller.sps_api_client.get.assert_called_once_with(
            controller.sps_api_base_url.format(spsId=lastSpsId))

        self.assertIsNone(responder['Akamai']['cert_domain'])
        self.assertEqual(
            'create_in_progress',
            responder['Akamai']['extra_info']['status']
        )
        self.assertEqual(
            'San cert request for www.abc.com has been enqueued.',
            responder['Akamai']['extra_info']['action']
        )

        mod_san_q = self.driver.mod_san_queue

        mod_san_q.enqueue_mod_san_request.assert_called_once_with(
            json.dumps(ssl_certificate.load_from_json(data).to_dict())
        )

    def test_cert_create_domain_exists_on_san(self):

        data = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        self.mock_get_sans_by_host.return_value = [
            data["domain_name"]
        ]

        controller = certificates.CertificateController(self.driver)

        responder = controller.create_certificate(
            ssl_certificate.load_from_json(data),
            True
        )

        self.assertIsNone(responder['Akamai']['cert_domain'])
        self.assertEqual(
            'failed',
            responder['Akamai']['extra_info']['status']
        )
        self.assertEqual(
            'Domain www.abc.com already exists on san cert 0.',
            responder['Akamai']['extra_info']['action']
        )
