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

from poppy.distributed_task.taskflow.flow import create_ssl_certificate
from poppy.distributed_task.taskflow.flow import delete_ssl_certificate
from poppy.manager import base
from poppy.model.helpers import domain
from poppy.transport.validators import helpers as validators


class DefaultSSLCertificateController(base.SSLCertificateController):

    def __init__(self, manager):
        super(DefaultSSLCertificateController, self).__init__(manager)

        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller)
        self.storage_controller = self._driver.storage.services_controller
        self.flavor_controller = self._driver.storage.flavors_controller

    def create_ssl_certificate(self, project_id, cert_obj):

        if (not validators.is_valid_domain_name(cert_obj.domain_name)) or \
                (validators.is_root_domain(
                    domain.Domain(cert_obj.domain_name).to_dict())):
            # here created a http domain object but it does not matter http or
            # https
            raise ValueError('%s must be a valid non-root domain' %
                             cert_obj.domain_name)

        try:
            flavor = self.flavor_controller.get(cert_obj.flavor_id)
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        try:
            self.storage_controller.create_cert(
                project_id,
                cert_obj)
        # ValueError will be raised if the cert_info has already existed
        except ValueError as e:
            raise e

        providers = [p.provider_id for p in flavor.providers]
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': project_id,
            'cert_obj_json': json.dumps(cert_obj.to_dict())
        }
        self.distributed_task_controller.submit_task(
            create_ssl_certificate.create_ssl_certificate,
            **kwargs)
        return kwargs

    def delete_ssl_certificate(self, project_id, domain_name,
                               cert_type):
        kwargs = {
            'project_id': project_id,
            'domain_name': domain_name,
            'cert_type': cert_type
        }
        self.distributed_task_controller.submit_task(
            delete_ssl_certificate.delete_ssl_certificate,
            **kwargs)
        return kwargs

    def get_certs_info_by_domain(self, domain_name, project_id):
        try:
            certs_info = self.storage_controller.get_certs_by_domain(
                domain_name=domain_name,
                project_id=project_id)
            if not certs_info:
                raise ValueError("certificate information"
                                 "not found for {0} ".format(domain_name))

            return certs_info

        except ValueError as e:
            raise e

    def get_akamai_san_retry_list(self):
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            res = akamai_driver.mod_san_queue.traverse_queue()
        else:
            # if not using akamai driver just return an empty list
            return []
        res = [json.loads(r) for r in res]
        return [
            (r['domain_name'], r['project_id'])
            for r in res
        ]
