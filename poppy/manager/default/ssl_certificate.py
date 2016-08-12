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

import itertools
import json

from oslo_context import context as context_utils
from oslo_log import log

from poppy.common import errors
from poppy.distributed_task.taskflow.flow import create_ssl_certificate
from poppy.distributed_task.taskflow.flow import delete_ssl_certificate
from poppy.distributed_task.taskflow.flow import recreate_ssl_certificate
from poppy.manager import base
from poppy.model.helpers import domain
from poppy.model import ssl_certificate
from poppy.transport.validators import helpers as validators

LOG = log.getLogger(__name__)


class DefaultSSLCertificateController(base.SSLCertificateController):

    def __init__(self, manager):
        super(DefaultSSLCertificateController, self).__init__(manager)

        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller
        )
        self.storage = self._driver.storage.certificates_controller
        self.service_storage = self._driver.storage.services_controller
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
            self.storage.create_certificate(
                project_id,
                cert_obj
            )
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

    def delete_ssl_certificate(self, project_id, domain_name, cert_type):
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
            certs_info = self.storage.get_certs_by_domain(
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
        # For other providers san_retry_list implementation goes here
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
            service_obj = self.service_storage\
                .get_service_details_by_domain_name(r['domain_name'])
            if service_obj is None and r.get('validate_service', True):
                raise LookupError(u'Domain {0} does not exist on any service, '
                                  'are you sure you want to proceed request, '
                                  '{1}? You can set validate_service to False '
                                  'to retry this san-retry request forcefully'.
                                  format(r['domain_name'], r))

            cert_for_domain = self.storage.get_certs_by_domain(
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
        res, deleted = [], []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            orig = [json.loads(r) for r in
                    akamai_driver.mod_san_queue.traverse_queue()]
            res = [json.loads(r) for r in
                   akamai_driver.mod_san_queue.put_queue_data(new_queue_data)]

            deleted = tuple(x for x in orig if x not in res)

        # other provider's retry-list implementation goes here
        return res, deleted

    def rerun_san_retry_list(self):
        run_list = []
        ignore_list = []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            retry_list = []
            while len(akamai_driver.mod_san_queue.mod_san_queue_backend) > 0:
                res = akamai_driver.mod_san_queue.dequeue_mod_san_request()
                retry_list.append(json.loads(res.decode('utf-8')))

            # remove duplicates
            # see http://bit.ly/1mX2Vcb for details
            def remove_duplicates(data):
                """Remove duplicates from the data (normally a list).

                The data must be sortable and have an equality operator
                """
                data = sorted(data)
                return [k for k, _ in itertools.groupby(data)]
            retry_list = remove_duplicates(retry_list)

            # double check in POST. This check should really be first done in
            # PUT
            for r in retry_list:
                err_state = False
                service_obj = self.service_storage\
                    .get_service_details_by_domain_name(r['domain_name'])
                if service_obj is None and r.get('validate_service', True):
                    err_state = True
                    LOG.error(
                        u'Domain {0} does not exist on any service, are you '
                        'sure you want to proceed request, {1}? You can set '
                        'validate_service to False to retry this san-retry '
                        'request forcefully'.format(r['domain_name'], r)
                    )
                elif (
                    service_obj is not None and
                    service_obj.operator_status.lower() == 'disabled'
                ):
                    err_state = True
                    LOG.error(
                        u'The service for domain {0} is disabled.'
                        'No certificates will be created for '
                        'service {1} while it remains in {2} operator_status'
                        'request forcefully'.format(
                            r['domain_name'],
                            service_obj.service_id,
                            service_obj.operator_status
                        )
                    )

                cert_for_domain = self.storage.get_certs_by_domain(
                    r['domain_name'])
                if cert_for_domain != []:
                    if cert_for_domain.get_cert_status() == "deployed":
                        err_state = True
                        LOG.error(
                            u'Certificate on {0} has already been provisioned '
                            'successfully.'.format(r['domain_name']))

                if err_state is False:
                    run_list.append(r)
                else:
                    ignore_list.append(r)
                    if not r.get('validate_service', True):
                        # validation is False, send ignored retry_list
                        # object back to queue
                        akamai_driver.mod_san_queue.enqueue_mod_san_request(
                            json.dumps(r)
                        )
                    LOG.warn(
                        "{0} was skipped because it failed validation.".format(
                            r['domain_name']
                        )
                    )

            for cert_obj_dict in run_list:
                try:
                    cert_obj = ssl_certificate.SSLCertificate(
                        cert_obj_dict['flavor_id'],
                        cert_obj_dict['domain_name'],
                        'san',
                        project_id=cert_obj_dict['project_id']
                    )

                    cert_for_domain = (
                        self.storage.get_certs_by_domain(
                            cert_obj.domain_name,
                            project_id=cert_obj.project_id,
                            flavor_id=cert_obj.flavor_id,
                            cert_type=cert_obj.cert_type))
                    if cert_for_domain == []:
                        pass
                    else:
                        # If this cert has been deployed through manual
                        # process we ignore the rerun process for this entry
                        if cert_for_domain.get_cert_status() == 'deployed':
                            continue
                    # rerun the san process
                    try:
                        flavor = self.flavor_controller.get(cert_obj.flavor_id)
                    # raise a lookup error if the flavor is not found
                    except LookupError as e:
                        raise e

                    providers = [p.provider_id for p in flavor.providers]
                    kwargs = {
                        'project_id': cert_obj.project_id,
                        'domain_name': cert_obj.domain_name,
                        'cert_type': 'san',
                        'providers_list_json': json.dumps(providers),
                        'cert_obj_json': json.dumps(cert_obj.to_dict()),
                        'enqueue': False,
                    }
                    self.distributed_task_controller.submit_task(
                        recreate_ssl_certificate.recreate_ssl_certificate,
                        **kwargs)
                except Exception as e:
                    # When exception happens we log it and re-queue this
                    # request
                    LOG.exception(e)
                    run_list.remove(cert_obj_dict)
                    ignore_list.append(cert_obj_dict)
                    akamai_driver.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj_dict)
                    )
        # For other providers post san_retry_list implementation goes here
        else:
            # if not using akamai driver just return summary of run list and
            # ignore list
            pass

        return run_list, ignore_list

    def get_san_cert_configuration(self, san_cert_name):
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            if san_cert_name not in akamai_driver.san_cert_cnames:
                raise ValueError(
                    "%s is not a valid san cert, valid san certs are: %s" %
                    (san_cert_name, akamai_driver.san_cert_cnames))
            res = akamai_driver.cert_info_storage.get_cert_config(
                san_cert_name
            )
        else:
            # if not using akamai driver just return an empty list
            res = {}

        return res

    def update_san_cert_configuration(self, san_cert_name, new_cert_config):
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            if san_cert_name not in akamai_driver.san_cert_cnames:
                raise ValueError(
                    "%s is not a valid san cert, valid san certs are: %s" %
                    (san_cert_name, akamai_driver.san_cert_cnames))
            akamai_driver = self._driver.providers['akamai'].obj
            # given the spsId, determine the most recent jobId
            # and persist the jobId
            if new_cert_config.get('spsId') is not None:
                resp = akamai_driver.sps_api_client.get(
                    akamai_driver.akamai_sps_api_base_url.format(
                        spsId=new_cert_config['spsId']
                    ),
                )
                if resp.status_code != 200:
                    raise RuntimeError(
                        'SPS GET Request failed. Exception: {0}'.format(
                            resp.text
                        )
                    )
                else:
                    resp_json = resp.json()
                    new_cert_config['jobId'] = (
                        resp_json['requestList'][0]['jobId']
                    )
            res = akamai_driver.cert_info_storage.update_cert_config(
                san_cert_name, new_cert_config)
        else:
            # if not using akamai driver just return an empty list
            res = {}

        return res

    def get_san_cert_hostname_limit(self):
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            res = akamai_driver.cert_info_storage.get_san_cert_hostname_limit()
            res = {'san_cert_hostname_limit': res}
        else:
            # if not using akamai driver just return an empty list
            res = {'san_cert_hostname_limit': 0}

        return res

    def set_san_cert_hostname_limit(self, request_json):
        if 'akamai' in self._driver.providers:
            try:
                new_limit = request_json['san_cert_hostname_limit']
            except Exception as exc:
                LOG.error("Error attempting to update san settings {0}".format(
                    exc
                ))
                raise ValueError('Unknown setting!')

            akamai_driver = self._driver.providers['akamai'].obj
            res = akamai_driver.cert_info_storage.set_san_cert_hostname_limit(
                new_limit
            )
        else:
            # if not using akamai driver just return an empty list
            res = 0

        return res

    def get_certs_by_status(self, status):
        certs_by_status = self.storage.get_certs_by_status(status)

        return certs_by_status

    def update_certificate_status(self, domain_name, certificate_updates):
        certificate_old = self.storage.get_certs_by_domain(domain_name)
        if not certificate_old:
            raise ValueError(
                "certificate information not found for {0} ".format(
                    domain_name
                )
            )

        try:
            if (
                certificate_updates.get("op") == "replace" and
                certificate_updates.get("path") == "status" and
                certificate_updates.get("value") is not None
            ):
                if (
                    certificate_old.get_cert_status() !=
                    certificate_updates.get("value")
                ):
                    new_cert_details = certificate_old.cert_details
                    # update the certificate for the first provider akamai
                    # this logic changes when multiple certificate providers
                    # are supported
                    first_provider = list(new_cert_details.keys())[0]
                    first_provider_cert_details = (
                        list(new_cert_details.values())[0]
                    )

                    first_provider_cert_details["extra_info"][
                        "status"] = certificate_updates.get("value")

                    new_cert_details[first_provider] = json.dumps(
                        first_provider_cert_details
                    )

                    self.storage.update_certificate(
                        certificate_old.domain_name,
                        certificate_old.cert_type,
                        certificate_old.flavor_id,
                        new_cert_details
                    )
        except Exception as e:
            LOG.error(
                "Something went wrong during certificate update: {0}".format(
                    e
                )
            )
            raise errors.CertificateStatusUpdateError(e)
