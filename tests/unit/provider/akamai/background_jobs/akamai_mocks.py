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
import random
import uuid

import json
import mock

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model import service
from poppy.model import ssl_certificate


class MockBootStrap(mock.Mock):

    def __init__(self, conf):
        super(MockBootStrap, self).__init__()

    @property
    def manager(self):
        return MockManager()


class MockProviderDetails(mock.Mock):

    def __init__(self, service_id):
        super(MockProviderDetails, self).__init__()
        self.service_id = service_id

    def __getitem__(self, provider_name):
        akamai_provider_detail_mock = mock.Mock()
        akamai_provider_detail_mock.provider_service_id = ''.join([
            '[{"protocol":',
            ' "https", "certificate": ',
            '"san", "policy_name": "blog.testabc.com"}]'])
        akamai_provider_detail_mock.status = 'deployed'
        return akamai_provider_detail_mock


class MockManager(mock.Mock):
    def __init__(self):
        super(MockManager, self).__init__()

    @property
    def providers(self):
        return self.get_providers()

    @staticmethod
    def get_providers():
        akamai_mock_provider = mock.Mock()
        akamai_mock_provider_obj = mock.Mock()
        akamai_mock_provider_obj.service_controller = mock.Mock()
        akamai_mock_provider_obj.akamai_conf = {
            'property_id': 'prp_12345',
            'contract_id': "B-ABCDE",
            'group_id': 12345
        }
        akamai_mock_provider_obj.akamai_sps_api_client = MockSPSAPIClient()
        akamai_mock_provider_obj.akamai_papi_api_client = MockPapiAPIClient()
        akamai_mock_provider_obj.akamai_sps_api_base_url = (
            'https://mybaseurl.net/config-secure-provisioning-service/'
            'v1/sps-requests/{spsId}?'
            'contractId=None&groupId=None')
        akamai_mock_provider_obj.akamai_papi_api_base_url = (
            'https://mybaseurl.net/papi/v0/{middle_part}/'
            '?contractId=ctr_None&groupId=grp_None')
        akamai_mock_provider_obj.san_mapping_queue.\
            traverse_queue.return_value = []
        akamai_mock_provider.obj = akamai_mock_provider_obj
        providers = {
            'akamai': akamai_mock_provider,
        }
        return providers

    @property
    def services_controller(self):
        return self.get_services_controller()

    @staticmethod
    def get_ssl_certificate_controller():
        sc = mock.Mock()
        sc.ssl_certificate_controller = MockStorageController()
        return sc

    @staticmethod
    def get_services_controller():
        sc = mock.Mock()
        sc.storage_controller = MockStorageController()
        return sc


class MockStorageController(mock.Mock):

    def get_certs_by_domain(self, domain_name, project_id=None,
                            flavor_id=None,
                            cert_type=None):

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
                        u'akamai_spsId': str(random.randint(1, 100000)),
                        u'create_at': u'2015-09-29 16:09:12.429147',
                        u'san cert': u'secure2.san1.test_123.com',
                        u'status': u'create_in_progress'}
                    }
            }
        )

    def get_service_details_by_domain_name(self, domain_name,
                                           project_id=None):
        r = service.Service(
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            [domain.Domain('wiki.cc', 'https', 'shared')],
            [origin.Origin('mysite.com')],
            "strawberry")
        r.provider_details = MockProviderDetails(r.service_id)
        return r


class MockPapiAPIClient(mock.Mock):
    def __init__(self):
        super(MockPapiAPIClient, self).__init__()
        self.response_200 = mock.Mock(status_code=200)

    def get(self, url):
        if 'hostnames' in url and 'versions' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-ABCDE",
                "contractId": "B-ABCDE",
                "groupId": "grp_12345",
                "propertyId": "prp_12345",
                "propertyName": "ssl.san.test_123.com_pm",
                "propertyVersion": 2,
                "etag": str(uuid.uuid4()),
                "hostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "cnameFrom": "www.testxxx.com",
                        "cnameTo": "ssl.test_123.com.edge_host_test.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1126816",
                        "cnameFrom": "secure.san2.test_789.com",
                        "cnameTo": "secure.test_456.com.edge_host_test.net"
                    }]
                }
            })
            self.response_200.status_code = 200
            return self.response_200
        if 'edgehostnames' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-ABCDE",
                "contractId": "B-ABCDE",
                "groupId": "grp_12345",
                "edgeHostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "domainPrefix": "secure1.san1.test_123.com",
                        "domainSuffix": "edge_host_test.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure1.san1.test_123.com"
                                              ".edge_host_test.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1159587",
                        "domainPrefix": "secure2.san1.test_123.com",
                        "domainSuffix": "edge_host_test.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure2.san1.test_123.com"
                                              ".edge_host_test.net"
                    }]
                }
            })
            self.response_200.status_code = 200
            return self.response_200
        if 'activations' in url:
            self.response_200.text = json.dumps({
                "activationId": "atv_2511473",
                "status": "SUCCESS"
            })
        if 'versions' in url:
            self.response_200.text = json.dumps({
                "propertyId": "prp_12345",
                "propertyName": "secure.test_123.com_pm",
                "accountId": "act_1-ABCDE",
                "contractId": "B-ABCDE",
                "groupId": "grp_12345",
                "versions": {
                    "items": [{
                        "propertyVersion": 1,
                        "etag": str(uuid.uuid4()),
                        "productionStatus": "ACTIVE",
                    }]
                }
            })
        else:
            self.response_200.text = json.dumps({
                "properties": {
                    "items": [{
                        "accountId": "act_1-ABCDE",
                        "contractId": "B-ABCDE",
                        "groupId": "grp_12345",
                        "propertyId": "prp_12345",
                        "propertyName": "secure.test_123.com_pm",
                        "latestVersion": 2,
                        "stagingVersion": 2,
                        "productionVersion": 1
                    }]
                }
            })
        self.response_200.status_code = 200
        return self.response_200

    def post(self, url, data=None, headers=None):
        if 'activations' in url:
            self.response_200.status_code = 201
            self.response_200.text = json.dumps({
                "activationLink": "/papi/v0/properties/prp_227429/"
                                  "activations/atv_2511473?contractId"
                                  "=ctr_C-2M6JYA&groupId=grp_12345",
                'warnings': []
            })
        if 'versions' in url:
            self.response_200.status_code = 201
        return self.response_200

    def put(self, url, data=None, headers=None):
        if 'hostnames' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-ABCDE",
                "contractId": "B-ABCDE",
                "groupId": "grp_12345",
                "propertyId": "prp_12345",
                "propertyName": "ssl.san.test_123.com_pm",
                "propertyVersion": 2,
                "etag": str(uuid.uuid4()),
                "hostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "cnameFrom": "secure.san1.test_789.com",
                        "cnameTo": "ssl.test_123.com.edge_host_test.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1126816",
                        "cnameFrom": "secure.san2.test_789.com",
                        "cnameTo": "secure.test_456.com.edge_host_test.net"
                    },  {
                        'cnameTo': 'secure.test_7891.com.edge_host_test.net',
                        'cnameFrom': 'www.blogyyy.com',
                        'edgeHostnameId': 'ehn_1126816',
                        'cnameType': u'EDGE_HOSTNAME'
                    }, {
                        'cnameTo': u'secure.test_7891.com.edge_host_test.net',
                        'cnameFrom': u'www.testxxx.com',
                        'edgeHostnameId': u'ehn_1126816',
                        'cnameType': u'EDGE_HOSTNAME'
                    }]
                }
            })
        return self.response_200


class MockSPSAPIClient(mock.Mock):
    def __init__(self):
        super(MockSPSAPIClient, self).__init__()
        self.response_200 = mock.Mock(status_code=200)

    def get(self, url):
        self.response_200.text = json.dumps({
            "requestList":
                [{"resourceUrl": "/config-secure-provisioning-service/"
                                 "v1/sps-requests/1849",
                    "parameters": [{
                        "name": "cnameHostname",
                        "value": "secure.san3.test_123.com"
                        }, {"name": "createType", "value": "san"},
                        {"name": "csr.cn",
                         "value": "secure.san3.test_123.com"},
                        {"name": "csr.c", "value": "US"},
                        {"name": "csr.st", "value": "TX"},
                        {"name": "csr.l", "value": "San Antonio"},
                        {"name": "csr.o", "value": "Rackspace US Inc."},
                        {"name": "csr.ou", "value": "IT"},
                        {"name": "csr.sans",
                         "value": "secure.san3.test_123.com"},
                        {"name": "organization-information.organization-name",
                         "value": "Rackspace US Inc."},
                        {"name": "organization-information.address-line-one",
                         "value": "1 Fanatical Place"},
                        {"name": "organization-information.city",
                         "value": "San Antonio"}],
                 "lastStatusChange": "2015-03-19T21:47:10Z",
                    "spsId": random.randint(1, 10000),
                    "status": "SPS Request Complete",
                    "jobId": random.randint(1, 100000)}]})
        self.response_200.status_code = 200
        return self.response_200

    def post(self, url, data=None, headers=None):
        self.response_200.status_code = 202
        self.response_200.text = json.dumps({
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
        return self.response_200

    def put(self, url, data=None, headers=None):
        return self.response_200
