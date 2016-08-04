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

import json

from oslo_config import cfg
from oslo_log import log
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.transport.pecan.models.request import ssl_certificate


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class GetCertInfoTask(task.Task):
    default_provides = "cert_obj_json"

    def execute(self, domain_name, cert_type, flavor_id, project_id):
        service_controller, self.ssl_certificate_manager = \
            memoized_controllers.task_controllers('poppy', 'ssl_certificate')
        self.storage = self.ssl_certificate_manager.storage

        res = self.storage.get_certs_by_domain(
            domain_name, project_id=project_id,
            flavor_id=flavor_id, cert_type=cert_type)
        if res is None:
            return ""
        return json.dumps(res.to_dict())


class CheckCertStatusTask(task.Task):
    default_provides = "status_change_to"

    def __init__(self):
        super(CheckCertStatusTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj

    def execute(self, cert_obj_json):
        if cert_obj_json != "":
            cert_obj = ssl_certificate.load_from_json(
                json.loads(cert_obj_json))
            latest_sps_id = cert_obj.cert_details['Akamai']['extra_info'].get(
                'akamai_spsId')
            current_status = cert_obj.cert_details['Akamai']['extra_info'].get(
                'status')

            if latest_sps_id is None:
                return current_status

            resp = self.akamai_driver.akamai_sps_api_client.get(
                self.akamai_driver.akamai_sps_api_base_url.format(
                    spsId=latest_sps_id
                )
            )

            if resp.status_code != 200:
                raise RuntimeError('SPS API Request Failed'
                                   'Exception: %s' % resp.text)

            sps_request_info = json.loads(resp.text)['requestList'][0]
            status = sps_request_info['status']
            workFlowProgress = sps_request_info.get(
                'workflowProgress')

            # This SAN Cert is on pending status
            if status == 'SPS Request Complete':
                LOG.info("SPS completed for %s..." %
                         cert_obj.get_san_edge_name())
                return "deployed"
            elif status == 'edge host already created or pending':
                if workFlowProgress is not None and \
                        'error' in workFlowProgress.lower():
                    LOG.info("SPS Pending with Error:" %
                             workFlowProgress)
                    return "failed"
                else:
                    return "deployed"
            elif status == 'CPS cancelled':
                return "cancelled"
            else:
                LOG.info(
                    "SPS Not completed for domain {0}, san_cert {1}. "
                    "Found status {2}. "
                    "Returning certificate object to Queue.".format(
                        cert_obj.domain_name,
                        cert_obj.get_san_edge_name(),
                        status
                    )
                )
                # convert cert_obj_json from unicode -> string
                # before enqueue
                self.akamai_driver.san_mapping_queue.enqueue_san_mapping(
                    json.dumps(cert_obj.to_dict()))
                return ""


class UpdateCertStatusTask(task.Task):

    def __init__(self):
        super(UpdateCertStatusTask, self).__init__()
        service_controller, self.ssl_certificate_manager = \
            memoized_controllers.task_controllers('poppy', 'ssl_certificate')
        self.storage_controller = (
            self.ssl_certificate_manager.storage
        )
        self.service_storage = service_controller.storage_controller

    def execute(self, project_id, cert_obj_json, status_change_to):
        if cert_obj_json != "":
            cert_obj = ssl_certificate.load_from_json(
                json.loads(cert_obj_json)
            )
            cert_details = cert_obj.cert_details

            if status_change_to != "":
                cert_details['Akamai']['extra_info']['status'] = (
                    status_change_to)
                cert_details['Akamai'] = json.dumps(cert_details['Akamai'])
                self.storage_controller.update_certificate(
                    cert_obj.domain_name,
                    cert_obj.cert_type,
                    cert_obj.flavor_id,
                    cert_details
                )

                service_obj = (
                    self.service_storage.
                    get_service_details_by_domain_name(cert_obj.domain_name)
                )
                # Update provider details
                if service_obj is not None:
                    service_obj.provider_details['Akamai'].\
                        domains_certificate_status.\
                        set_domain_certificate_status(cert_obj.domain_name,
                                                      status_change_to)
                    self.service_storage.update_provider_details(
                        project_id,
                        service_obj.service_id,
                        service_obj.provider_details
                    )
            else:
                pass
