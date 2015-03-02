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


class PrepareMODSANCertTask(task.Task):
    default_provides = 'san_cert_mod_input'

    def __init__(self):
        super(PrepareMODSANCertTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller
        self.all_services = self.sc.dequeue_all_add_san_cert_service()
        self.all_services = [json.loads(service) for service
                             in self.all_services]
        self.added_services = [service[1:] for service in self.all_services
                               if service[0] == "add"]
        self.removed_services = [service[1:] for service in
                                 self.all_services
                                 if service[0] == "remove"]
        # This doesn't do anything for now

    def execute(self):
        # make the modify san-cert request in this task
        san_cert_info = self._pick_san_cert()

        resp = self.akamai_driver.akamai_sps_api_client.get(
            self.akamai_driver.akamai_sps_api_base_url.format(
                spsId=san_cert_info['spsId'][-1]) + "&information=true",
        )
        if resp.status_code != 200:
            raise RuntimeError('SPS Request failed.'
                               'Exception: %s' % resp.text)

        resp_dict = json.loads(resp.text)
        request_params = resp_dict['requestList'][0]['parameters']
        existing_domains = [p['value'] for p in request_params
                            if p['name'] in ['add.sans']]

        all_domains = self._gather_service_hosts(self.all_services)
        added_domains = list(set([domain[2] for domain in all_domains
                             if domain[0] == 'add']))
        added_domains.extend(existing_domains)
        san_cert_info['hostCount'] = len(added_domains)
        san_cert_mod_input = {}
        san_cert_mod_input['san_cert_info'] = san_cert_info
        san_cert_mod_input['add.sans'] = added_domains
        # Add these extra information for failer/requeue info
        san_cert_mod_input['added_services'] = self.added_services
        # This param is not useful yet, but potentially be useful
        san_cert_mod_input['removed_services'] = self.removed_services
        san_cert_mod_input['all_services'] = self.all_services
        san_cert_mod_input['all_domains'] = all_domains
        return san_cert_mod_input

    def _pick_san_cert(self):
        san_cert_list = json.load(open(SAN_CERT_RECORDS_FILE_PATH))
        return san_cert_list[0]

    def _gather_service_hosts(self, all_services):
        result = all_services
        return result

    def revert(self, **kwargs):
        # requeue service here
        self.sc.requeue_mod_san_cert_services(
            [json.dumps(service) for service in self.all_services])


class MODSANCertRequestTask(task.Task):
    """requires san_cert_mod_post_data"""

    def __init__(self):
        super(MODSANCertRequestTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller

    def execute(self, san_cert_mod_input):
        self.added_services = [service[1] for service in
                               san_cert_mod_input.get('added_services', [])]
        self.removed_services = [service[1] for service in
                                 san_cert_mod_input.get('removed_services',
                                                        [])]
        self.all_servcies = san_cert_mod_input.get('all_services', [])
        self.all_domains = san_cert_mod_input.get('all_domains', [])

        san_cert_info = san_cert_mod_input['san_cert_info']
        string_data = self._get_mod_san_cert_post_data(san_cert_mod_input)

        #################
        resp = self.akamai_driver.akamai_sps_api_client.post(
            self.akamai_driver.akamai_sps_api_base_url.format(spsId=""),
            data=string_data
        )
        if resp.status_code != 202:
            raise RuntimeError('SPS Request failed.'
                               'Exception: %s' % resp.text)
        else:
            resp_dict = json.loads(resp.text)
            # adding the spsId to this SAN Cert info list
            self._update_san_cert(san_cert_info, resp_dict['spsId'])
            # enqueue to status queue
            hosts_message = []
            for domain_action_info in self.all_domains:
                action, service_info, domain = domain_action_info
                hosts_message.append((action, {
                    "cnameType": "EDGE_HOSTNAME",
                    "edgeHostnameId": san_cert_info['edgeHostnameId'],
                    "cnameFrom": domain,
                    'cnameTo': san_cert_info['cnameHostname'] + '.edgekey.net'
                }))
                LOG.info("Affected poppy services: %s" % str(service_info))
            self.sc.enqueue_papi_update_job('hosts',
                                            json.dumps(hosts_message),
                                            ({'SPSStatusCheck':
                                                resp_dict['spsId']},
                                             self.added_services))

    def revert(self, san_cert_mod_input, **kwargs):
        # requeue service here
        self.sc.requeue_mod_san_cert_services(
            [json.dumps(service) for service in self.all_services])

    def _update_san_cert(self, san_cert_info, spsId):
        # Needed this step because:
        # It is need to keep track of how many hosts/domains are there in a
        # SAN Cert
        san_cert_list = json.load(open(SAN_CERT_RECORDS_FILE_PATH))
        my_index = san_cert_list.index(san_cert_info)
        san_cert_list[my_index]['spsId'].append(spsId)
        # Write this piece of san cert info the SAN_CERT_RECORDS_FILE_PATH
        with open(SAN_CERT_RECORDS_FILE_PATH, 'w') as san_cert_file:
            json.dump(san_cert_list, san_cert_file)

    def _get_mod_san_cert_post_data(self, san_cert_mod_input):
        post_data = {
            'cnameHostname': (
                san_cert_mod_input['san_cert_info']['cnameHostname']),
            'jobId': san_cert_mod_input['san_cert_info']['jobId'],
            'issuer': san_cert_mod_input['san_cert_info']['issuer'],
            'createType': 'modSan',
            'ipVersion': san_cert_mod_input['san_cert_info']['ipVersion'],
            'slot-deployment.klass': (
                san_cert_mod_input['san_cert_info']['slot-deployment.klass']),
        }

        kv_list = ['%s=%s' % (k, v) for (k, v) in post_data.items()]
        kv_list.extend(['add.sans=%s' % domain
                        for domain
                        in san_cert_mod_input['add.sans']])
        string_post_data = '&'.join(kv_list)
        return string_post_data


if __name__ == "__main__":
    print(SAN_CERT_RECORDS_FILE_PATH)
