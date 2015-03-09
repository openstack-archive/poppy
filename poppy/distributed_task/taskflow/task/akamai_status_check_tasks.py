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


class StatusCheckAndUpdateTask(task.Task):

    def __init__(self):
        super(StatusCheckAndUpdateTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        service_controller = self.bootstrap_obj.manager.services_controller
        self.storage_controller = service_controller.storage_controller
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj
        self.akamai_conf = self.akamai_driver.akamai_conf
        self.status_check_info, self.services_list = None, None

    def execute(self):
        # use queue cache for revert requeue
        for i in range(0, self.sc.len_status_check_queue()):
            i
            status_check_queue_entry = self.sc.dequeue_status_check_queue()
            self.status_check_info, self.services_list = (
                status_check_queue_entry)
            LOG.info("Dequeue Status Check Job: %s\n %s" % (
                str(self.status_check_info),
                str(self.services_list)))
            # Key can only be either SPSStatusCheck or
            # PropertyActivation
            sps_success = activation_success = True
            for key in self.status_check_info:
                if key == 'SPSStatusCheck':
                    LOG.info("Start SPSStatusCheck: %s" %
                             self.status_check_info['SPSStatusCheck'])
                    spsId = self.status_check_info['SPSStatusCheck']
                    resp = self.akamai_driver.akamai_sps_api_client.get(
                        self.akamai_driver.akamai_sps_api_base_url.format(
                            spsId=spsId),
                    )
                    if resp.status_code != 200:
                        raise RuntimeError('SPS API Request Failed'
                                           'Exception: %s' % resp.text)
                    status = json.loads(resp.text)['requestList'][0]['status']
                    if status != 'SPS Request Complete':
                        LOG.info("SPS Not completed...")
                        sps_success = False
                        break
                elif key == 'PropertyActivation':
                    LOG.info("Start PropertyActivation check: %s" %
                             self.status_check_info['PropertyActivation'])
                    activationId = self.status_check_info['PropertyActivation']
                    resp = self.akamai_driver.akamai_papi_api_client.get(
                        self.akamai_driver.akamai_papi_api_base_url.format(
                            middle_part='properties/%s/activations/%s' % (
                                self.akamai_conf['property_id'],
                                str(activationId)))
                    )
                    # Akamai now has a issue, when status_code is 500, it couls
                    # also mean activation sucessful
                    if resp.status_code != 200 and resp.status_code != 500:
                        raise RuntimeError('PAPI API request failed.'
                                           'Exception: %s' % resp.text)

                    if resp.status_code == 200:
                        status = json.loads(resp.text)['status']
                        if status != 'SUCCESS':
                            LOG.info("Activation Not completed...")
                            activation_success = False
                    if resp.status_code == 500:
                        # else check if the latest version has been in
                        # production or staging yet
                        resp = self.akamai_driver.akamai_papi_api_client.get(
                            self.akamai_driver.akamai_papi_api_base_url.format(
                                middle_part='properties/%s' %
                                self.akamai_conf['property_id'])
                        )
                        if resp.status_code != 200:
                            raise RuntimeError('PAPI API request failed.'
                                               'Exception: %s' % resp.text)
                        else:
                            properties = json.loads(resp.text)['properties']
                            a_property = properties['items'][0]
                            latestVersion = a_property['latestVersion'] or 0
                            production_version = (
                                # a_property['productionVersion'] or -1
                                a_property['stagingVersion'] or -1
                                )
                            if not latestVersion == production_version:
                                LOG.info("Activation Not completed...")
                                activation_success = False
                                break
                            else:
                                LOG.info("Activation Completed...")
                                activation_success = True
            if (sps_success and activation_success):
                # sps and activation both successful, now can change service
                # status to deployed
                LOG.info('Status check: %s successful. Updating info...' %
                         str(self.status_check_info))
                self.update_service_list_status(self.services_list)
            else:
                # requeue this entry because one of the
                # status is not successful yet
                LOG.info('Status not completed yet.\n'
                         'Requeuing status check queue: %s' %
                         str(self.status_check_info))
                self.sc.enqueue_status_check_queue(
                    self.status_check_info, self.services_list)

    def update_service_list_status(self, services_list):
        # service list is a list of tuple, but this tulpe right now is in
        # the form of a json string
        # needs to handle secureHosts case, where we update the secureHosts
        # not poppy service
        if len(services_list) == 1 and (
                not isinstance(services_list[0], list)):
            # services_list[0][0] == "secureEdgeHost"
            services_list = [json.loads(service) for service in services_list]
            message = services_list[0][1]
            LOG.info('Update secureEdgeHost check: %s' % str(message))
            cert_info = {
                "cnameHostname": message["cnameHostname"],
                "jobID": message["jobID"],
                "ipVersion": "ipv4",
                "spsId": [message["spsId"]],
                "issuer": "cybertrust",
                "slot-deployment.klass": "esslType"}
            if message['certType'] == 'san':
                cert_info['issuer'] = 'symantec'
                cert_info['hostCount'] = 0
                self._update_san_cert_file(cert_info)
            else:
                # potentially do some custom cert housekeeping here
                pass
            LOG.info('Enqueue secureEdgeHost PAPI update job: %s'
                     % str(message))
            self.sc.enqueue_papi_update_job('secureEdgeHost',
                                            message)
            return

        # else update poppy services
        for project_info, domain in services_list:
            project_id, service_id = project_info
            LOG.info("domain: %s provision is completed..." % domain)
            try:
                service_obj = (
                    self.storage_controller.get(project_id, service_id))
            except ValueError:
                # if service gets deleted we just ignore it
                return
            provider_details = service_obj.provider_details
            # Just update Akamai's service detail to deployed
            provider_details.get('Akamai').status = u'deployed'
            self.storage_controller.update_provider_details(project_id,
                                                            service_id,
                                                            provider_details)

    def _update_san_cert_file(self, san_cert_info):
        # Needed this step because:
        # It is need to keep track of how many hosts/domains are there in a
        # SAN Cert
        LOG.info('New SAN Cert added: %s ' % str(san_cert_info))
        if len(open(SAN_CERT_RECORDS_FILE_PATH).read()) == 0:
            san_cert_list = [san_cert_info]
        else:
            san_cert_list = json.load(open(SAN_CERT_RECORDS_FILE_PATH))
            san_cert_list.append(san_cert_info)
        # Write this piece of san cert info the SAN_CERT_RECORDS_FILE_PATH
        with open(SAN_CERT_RECORDS_FILE_PATH, 'w') as san_cert_file:
            json.dump(san_cert_list, san_cert_file)

    def revert(self, **kwargs):
        # probably can implement a requeue_all to get all entries
        # on queue at once
        if self.status_check_info is not None and (
                self.services_list is not None):
            self.sc.enqueue_status_check_queue(self.status_check_info,
                                               self.services_list)
