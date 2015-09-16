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
        akamai_mock_provider = mock.Mock()
        akamai_mock_provider_obj = mock.Mock()
        akamai_mock_provider_obj.service_controller = mock.Mock()
        akamai_mock_provider_obj.akamai_conf = {
            'property_id': 'prp_226831',
            'contract_id': "C-2M6JYA",
            'group_id': 23174
        }
        akamai_mock_provider_obj.akamai_sps_api_client = MockSPSAPIClient()
        akamai_mock_provider_obj.akamai_papi_api_client = MockPapiAPIClient()
        akamai_mock_provider_obj.akamai_sps_api_base_url = (
            'https://akab-3r276kizolbgfqbi-6tnfu4jessqtn4b4.luna.akamaiapis.'
            'net/config-secure-provisioning-service/v1/sps-requests/{spsId}?'
            'contractId=None&groupId=None')
        akamai_mock_provider_obj.akamai_papi_api_base_url = (
            'https://akab-3r276kizolbgfqbi-6tnfu4jessqtn4b4.luna.akamaiapis.'
            'net/papi/v0/{middle_part}/?contractId=ctr_None&groupId=grp_None')
        akamai_mock_provider.obj = akamai_mock_provider_obj
        providers = {
            'akamai': akamai_mock_provider,
        }
        return providers

    @property
    def services_controller(self):
        sc = mock.Mock()
        sc.storage_controller = MockStorageController()
        return sc


class MockStorageController(mock.Mock):

    def get_cert_by_domain(self, domain_name, cert_type,
                           flavor_id, project_id):

        return ssl_certificate.SSLCertificate(
            "premium",
            "blog.testabc.com",
            "san",
            cert_details={
                'Akamai': {
                    u'cert_domain': u'secure2.san1.altcdn.com',
                    u'extra_info': {
                        u'action': u'Waiting for customer domain '
                                    'validation for blog.testabc.com',
                        u'akamai_spsId': 22231,
                        u'create_at': u'2015-09-29 16:09:12.429147',
                        u'san cert': u'secure2.san1.altcdn.com',
                        u'status': u'create_in_progress'}
                    }
            }
        )

    def get_service_details_by_domain_name(self, domain_name):
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
        if 'hostnames' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-RMX47R",
                "contractId": "ctr_C-2M6JYA",
                "groupId": "grp_23174",
                "propertyId": "prp_227429",
                "propertyName": "ssl.san.altcdn.com_pm",
                "propertyVersion": 2,
                "etag": "d68007973c8ef0ff8149dc180822d42f61e8c447",
                "hostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "cnameFrom": "www.testxxx.com",
                        "cnameTo": "ssl.altcdn.com.edgekey.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1126816",
                        "cnameFrom": "secure.san2.raxtest.com",
                        "cnameTo": "secure.raxcdn.com.edgekey.net"
                    }]
                }
            })
        if 'edgehostnames' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-RMX47R",
                "contractId": "ctr_C-2M6JYA",
                "groupId": "grp_23174",
                "edgeHostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "domainPrefix": "secure1.san1.altcdn.com",
                        "domainSuffix": "edgekey.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure1.san1.altcdn.com"
                                              ".edgekey.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1159587",
                        "domainPrefix": "secure2.san1.altcdn.com",
                        "domainSuffix": "edgekey.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure2.san1.altcdn.com"
                                              ".edgekey.net"
                    }]
                }
            })
        if 'activations' in url:
            self.response_200.text = json.dumps({
                "activationId": "atv_2511473",
                "status": "SUCCESS"
            })
        if 'versions' in url:
            self.response_200.text = json.dumps({
                "propertyId": "prp_226818",
                "propertyName": "secure.altcdn.com_pm",
                "accountId": "act_1-RMX47R",
                "contractId": "ctr_C-2M6JYA",
                "groupId": "grp_23174",
                "versions": {
                    "items": [{
                        "propertyVersion": 1,
                        "etag": "cb2dfd7a325d8b92874f8a68dfe81e97e54730da"
                    }]
                }
            })
        else:
            self.response_200.text = json.dumps({
                "properties": {
                    "items": [{
                        "accountId": "act_1-RMX47R",
                        "contractId": "ctr_C-2M6JYA",
                        "groupId": "grp_23174",
                        "propertyId": "prp_226818",
                        "propertyName": "secure.altcdn.com_pm",
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
                                  "=ctr_C-2M6JYA&groupId=grp_23174",
                'warnings': []
            })
        if 'versions' in url:
            self.response_200.status_code = 201
        return self.response_200

    def put(self, url, data=None, headers=None):
        if 'hostnames' in url:
            self.response_200.text = json.dumps({
                "accountId": "act_1-RMX47R",
                "contractId": "ctr_C-2M6JYA",
                "groupId": "grp_23174",
                "propertyId": "prp_227429",
                "propertyName": "ssl.san.altcdn.com_pm",
                "propertyVersion": 2,
                "etag": "d68007973c8ef0ff8149dc180822d42f61e8c447",
                "hostnames": {
                    "items": [{
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1052022",
                        "cnameFrom": "secure.san1.raxtest.com",
                        "cnameTo": "ssl.altcdn.com.edgekey.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1126816",
                        "cnameFrom": "secure.san2.raxtest.com",
                        "cnameTo": "secure.raxcdn.com.edgekey.net"
                    },  {
                        'cnameTo': 'secure.raxtest1.com.edgekey.net',
                        'cnameFrom': 'www.blogyyy.com',
                        'edgeHostnameId': 'ehn_1126816',
                        'cnameType': u'EDGE_HOSTNAME'
                    }, {
                        'cnameTo': u'secure.raxtest1.com.edgekey.net',
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
                        "value": "secure.san3.altcdn.com"
                        }, {"name": "createType", "value": "san"},
                        {"name": "csr.cn", "value": "secure.san3.altcdn.com"},
                        {"name": "csr.c", "value": "US"},
                        {"name": "csr.st", "value": "TX"},
                        {"name": "csr.l", "value": "San Antonio"},
                        {"name": "csr.o", "value": "Rackspace US Inc."},
                        {"name": "csr.ou", "value": "IT"},
                        {"name": "csr.sans",
                         "value": "secure.san3.altcdn.com"},
                        {"name": "organization-information.organization-name",
                         "value": "Rackspace US Inc."},
                        {"name": "organization-information.address-line-one",
                         "value": "1 Fanatical Place"},
                        {"name": "organization-information.city",
                         "value": "San Antonio"}],
                 "lastStatusChange": "2015-03-19T21:47:10Z",
                    "spsId": 1789,
                    "status": "SPS Request Complete",
                    "jobId": 44306}]})
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
