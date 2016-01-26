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

from oslo_context import context as context_utils

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
            'cert_obj_json': json.dumps(cert_obj.to_dict()),
            'context_dict': context_utils.get_current().to_dict()
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
            'cert_type': cert_type,
            'context_dict': context_utils.get_current().to_dict()
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

    def get_san_retry_list(self):
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            res = akamai_driver.mod_san_queue.traverse_queue()
        # For other providers san_retry_list implementaion goes here
        else:
            # if not using akamai driver just return an empty list
            return []
        res = [json.loads(r) for r in res]
        return [
            {"domain_name": r['domain_name'],
             "project_id":  r['project_id'],
             "flavor_id":   r['flavor_id'],
             "validate_service": r.get('validate_service', True)}
            for r in res
        ]

    def update_san_retry_list(self, queue_data_list):
        for r in queue_data_list:
            service_obj = self.storage_controller\
                .get_service_details_by_domain_name(r['domain_name'])
            if service_obj is None and r.get('validate_service', True):
                raise LookupError(u'Domain {0} does not exist on any service, '
                                  'are you sure you want to proceed request, '
                                  '{1}? You can set validate_service to False '
                                  'to retry this san-retry request forcefully'.
                                  format(r['domain_name'], r))

            cert_for_domain = self.storage_controller.get_certs_by_domain(
                r['domain_name'])
            if cert_for_domain != []:
                if cert_for_domain.get_cert_status() == "deployed":
                    raise ValueError(u'Cert on {0} already exists'.
                                     format(r['domain_name']))

        new_queue_data = [
            json.dumps({'flavor_id':   r['flavor_id'],  # flavor_id
                        'domain_name': r['domain_name'],    # domain_name
                        'project_id': r['project_id'],
                        'validate_service': r.get('validate_service', True)})
            for r in queue_data_list
        ]
        res, diff = [], []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            orig = [json.loads(r) for r in
                    akamai_driver.mod_san_queue.traverse_queue()]
            res = [json.loads(r) for r in
                   akamai_driver.mod_san_queue.put_queue_data(new_queue_data)]

            diff = tuple(x for x in res if x not in orig)
        # other provider's retry-list implementaiton goes here
        return res, diff
