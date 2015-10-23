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
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import ssl_certificate


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class GetCertInfoTask(task.Task):
    default_provides = "cert_obj_json"

    def execute(self, domain_name, cert_type, flavor_id, project_id):
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')
        res = self.storage_controller.get_certs_by_domain(
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
            cert_obj = ssl_certificate.load_from_json(json.loads(cert_obj_json)
                                                      )
            latest_sps_id = cert_obj.cert_details['Akamai']['extra_info'].get(
                'akamai_spsId')

            if latest_sps_id is None:
                return ""

            resp = self.akamai_driver.akamai_sps_api_client.get(
                self.akamai_driver.akamai_sps_api_base_url.format(
                    spsId=latest_sps_id
                )
            )

            if resp.status_code != 200:
                raise RuntimeError('SPS API Request Failed'
                                   'Exception: %s' % resp.text)

            status = json.loads(resp.text)['requestList'][0]['status']

            # This SAN Cert is on pending status
            if status != 'SPS Request Complete':
                LOG.info("SPS Not completed for %s..." %
                         self.cert)
                return ""
            else:
                LOG.info("SPS completed for %s..." %
                         cert_obj.get_san_edge_name())
                return "deployed"


class UpdateCertStatusTask(task.Task):

    def __init__(self):
        super(UpdateCertStatusTask, self).__init__()
        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

    def execute(self, project_id, cert_obj_json, status_change_to):
        if cert_obj_json != "":
            cert_obj = ssl_certificate.load_from_json(json.loads(cert_obj_json)
                                                      )
            cert_details = cert_obj.cert_details

            if status_change_to == "deployed":
                cert_details['Akamai']['extra_info']['status'] = 'deployed'
                cert_details['Akamai'] = json.dumps(cert_details['Akamai'])
                self.storage_controller.update_cert_info(cert_obj.domain_name,
                                                         cert_obj.cert_type,
                                                         cert_obj.flavor_id,
                                                         cert_details)

                service_obj = (
                    self.storage_controller.
                    get_service_details_by_domain_name(cert_obj.domain_name)
                )
                # Update provider details
                if service_obj is not None:
                    service_obj.provider_details['Akamai'].\
                        domains_certificate_status.\
                        set_domain_certificate_status(cert_obj.domain_name,
                                                      'deployed')
                    self.storage_controller.update_provider_details(
                        project_id,
                        service_obj.service_id,
                        service_obj.provider_details
                    )
            else:
                pass
