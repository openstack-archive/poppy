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
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)

        self.added_servcies = self.sc.dequeue_all_add_san_cert_service()
        # This doesn't do anything for now
        self.removed_services = self.sc.dequeue_all_add_san_cert_service()

    def execute(self):
        # make the modify san-cert request in this task
        san_cert_info = self.pick_san_cert()
        domains = self.gather_service_hosts(self.added_servcies,
                                            self.removed_services)
        san_cert_mod_input = {}
        san_cert_mod_input['san_cert_info'] = san_cert_info
        san_cert_mod_input['add.sans'] = domains
        # Add these extra information for failer/requeue info
        san_cert_mod_input['added_service'] = self.added_servcies
        # This param is not useful yet, but potentially be useful
        san_cert_mod_input['removed_services'] = self.removed_services
        return san_cert_mod_input

    def pick_san_cert(self):
        san_cert_list = json.load(file(SAN_CERT_RECORDS_FILE_PATH))
        return san_cert_list[0]

    def gather_service_hosts(self, added_servcies, removed_services):
        result = []
        for (project_id, service_id) in added_servcies:
            service_controller = self.bootstrap_obj.manager.services_controller
            storage_controller = service_controller.storage_controller
            service = storage_controller.get(project_id, service_id)
            pd = service.provider_detail.get('akamai', {})
            for i_id in pd.get('provider_service_id', []):
                if i_id.get('certification', None) == 'san':
                    # hosthname is the domain name
                    result.append(i_id.get('policy_name'))
        return result

    def revert(self):
        # requeue service here
        self.sc.requeue_mod_san_cert_services(
            self.added_servcies,
            self.removed_services)


class MODSANCertRequestTask(task.Task):
    """requires san_cert_mod_post_data"""

    def __init__(self):
        super(PrepareMODSANCertTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)

    def execute(self, san_cert_mod_input):
        self.added_service = san_cert_mod_input.pop('added_service')
        self.removed_services = san_cert_mod_input.pop('removed_services')

        san_cert_info = san_cert_mod_input['san_cert_info']
        string_data = self.get_mod_san_cert_post_data(san_cert_mod_input)

        akamai_driver = self.bootstrap_obj.manager.providers['akamai']
        #################
        resp = akamai_driver.akamai_sps_api_client.post(
            akamai_driver.akamai_sps_api_base_url.format(spsId=""),
            data=string_data
        )
        if resp.status_code != 200:
            raise RuntimeError('Issuing Mod SAN Cert request failed.'
                               'Exception: %s' % resp.text)
        else:
            resp_dict = json.loads(resp.text)
            # adding the spsId to this SAN Cert info list
            self.update_san_cert(san_cert_info, resp_dict['spsId'])
            # enqueue to status queue
            hosts_message = []
            for domain in san_cert_mod_input['add.sans']:
                hosts_message.append({
                    "cnameType": "EDGE_HOSTNAME",
                    "edgeHostnameId": san_cert_info['edgeHostnameId'],
                    "cnameFrom": domain,
                    'cnameTo': san_cert_info['cnameHostname'] + '.edgekey.net'
                })
            self.sc.enqueue_papi_update_job('hosts', json.dumps(hosts_message))

    def revert(self):
        # requeue service here
        self.sc.requeue_mod_san_cert_services(
            self.added_servcies,
            self.removed_services)

    def update_san_cert(self, san_cert_info, spsId):
        # Needed this step because:
        # It is need to keep track of how many hosts/domains are there in a
        # SAN Cert
        san_cert_list = json.load(file(SAN_CERT_RECORDS_FILE_PATH))
        my_index = san_cert_list.index(san_cert_info)
        san_cert_list[my_index]['spsId'].append(spsId)
        # Write this piece of san cert info the SAN_CERT_RECORDS_FILE_PATH
        with open(SAN_CERT_RECORDS_FILE_PATH, 'w') as san_cert_file:
            json.dump(san_cert_list, san_cert_file)

    def get_mod_san_cert_post_data(self, san_cert_mod_input):
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
                        in san_cert_mod_input['san_cert_info']['add.sans']])
        string_post_data = '&'.join(kv_list)
        return string_post_data


if __name__ == "__main__":
    print(SAN_CERT_RECORDS_FILE_PATH)
