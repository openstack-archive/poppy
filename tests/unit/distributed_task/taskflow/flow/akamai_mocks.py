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

import mock


added_services_list = [[u'add',
                        [u'000', u'f81f4459-ae02-4e3b-b36e-e4917adfe945']]]
removed_services_list = [[u'remove',
                          [u'000', u'4fe3fbab-a73f-459d-be8a-74f9ff82c147']]]

hosts_message = [["remove",
                  {"cnameTo": "secure.raxtest1.com.edgekey.net",
                   "cnameFrom": "www.testxxx.com",
                   "edgeHostnameId": "ehn_1126816",
                   "cnameType": "EDGE_HOSTNAME"}],
                 ["add",
                  {"cnameTo": "secure.raxtest1.com.edgekey.net",
                   "cnameFrom": "www.blogyyy.com",
                   "edgeHostnameId": "ehn_1126816",
                   "cnameType": "EDGE_HOSTNAME"}]]


class MockProviderDetails(mock.Mock):

    def __init__(self, service_id):
        super(MockProviderDetails, self).__init__()
        self.service_id = service_id

    def get(self, provider_name):
        akamai_provider_detail_mock = mock.Mock()
        if self.service_id == "f81f4459-ae02-4e3b-b36e-e4917adfe945":
            akamai_provider_detail_mock.provider_service_id = ''.join([
                '[{"protocol":',
                ' "https", "certificate": ',
                '"san", "policy_name": "www.blogyyy.com"}]'])
        elif self.service_id == "4fe3fbab-a73f-459d-be8a-74f9ff82c147":
            akamai_provider_detail_mock.provider_service_id = ''.join([
                '[{"protocol":',
                ' "https", "certificate": ',
                '"san", "policy_name": "www.testxxx.com"}]'])
        akamai_provider_detail_mock.status = 'create_in_progress'
        return akamai_provider_detail_mock


class MockBootStrap(mock.Mock):

    def __init__(self, conf):
        super(MockBootStrap, self).__init__()

    @property
    def manager(self):
        return MockManager()


class MockManager(mock.Mock):
    def __init__(self):
        super(MockManager, self).__init__()

    @property
    def distributed_task(self):
        return MockDistributedTask()

    @property
    def providers(self):
        akamai_mock_provider = mock.Mock()
        akamai_mock_provider_obj = mock.Mock
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

    def get(self, project_id, service_id):
        r = mock.Mock()
        r.provider_details = MockProviderDetails(service_id)
        return r


class MockDistributedTask(mock.Mock):
    def __init__(self):
        super(MockDistributedTask, self).__init__()

    @property
    def services_controller(self):
        return MockDistributedTaskServiceController()


class MockDistributedTaskServiceController(mock.Mock):

    def dequeue_all_add_san_cert_service(self):
        return ['["remove", ["000", "4fe3fbab-a73f-459d-be8a-74f9ff82c147"]]',
                '["add", ["000", "f81f4459-ae02-4e3b-b36e-e4917adfe945"]]']

    def dequeue_all_remove_san_cert_service(self):
        return removed_services_list

    def dequeue_all_papi_jobs(self):

        return [json.dumps({u'message': json.dumps(hosts_message),
                u'services_list_info': [
                # explaining of type data structure
                # services_list_info is used later to enqueue
                # the status check queue.
                # status check queue needs to have information as to
                # what status needs to check on, and what are
                # the associated services with this status check
                # as in Mod SAN Cert's case, there could be multiple
                # services with one SPS check
                    {u'SPSStatusCheck': 1789},
                    [u'["000", "f81f4459-ae02-4e3b-b36e-e4917adfe945"]',
                     u'["000", "4fe3fbab-a73f-459d-be8a-74f9ff82c147"]']],
                u'j_type': u'hosts'}),
                '{"message": {"cnameHostname": "secure.san2.raxtest.com", '
                '"spsId": 1789, "certType":"custom", "jobID": 44434}, '
                '"j_type": "secureEdgeHost"}']

    def len_status_check_queue(self):
        return 1

    def dequeue_status_check_queue(self):
        # return ({u'SPSStatusCheck': 1789,
        #          u'PropertyActivation': u'atv_2511473'},
        #         [u'["000", "f81f4459-ae02-4e3b-b36e-e4917adfe945"]',
        #          u'["000", "4fe3fbab-a73f-459d-be8a-74f9ff82c147"]'])
        return ({u'SPSStatusCheck': 1789},
                [u'["secureEdgeHost", '
                 '{"cnameHostname": "secure.san2.raxtest.com", '
                 '"spsId": 1789, "jobID": 44434}]'])


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
                        "domainPrefix": "secure.san2.raxtest.com",
                        "domainSuffix": "edgekey.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure.san2.raxtest.com"
                                              ".edgekey.net"
                    }, {
                        "cnameType": "EDGE_HOSTNAME",
                        "edgeHostnameId": "ehn_1159587",
                        "domainPrefix": "secure.san1.raxtest.com",
                        "domainSuffix": "edgekey.net",
                        "ipVersionBehavior": "IPV4",
                        "secure": True,
                        "edgeHostnameDomain": "secure.san1.raxtest.com"
                                              ".edgekey.net"
                    }]
                }
            })
        if 'activations' in url:
            self.response_200.text = json.dumps({
                "activationId": "atv_2511473",
                "status": "SUCCESS"
            })
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
                 "lastStatusChange": "2015-03-19T21:47:10Z",
                    "spsId": 1789,
                    "status": "SUCCESS",
                    "jobId": 44306}]})
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
