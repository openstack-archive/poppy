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

from oslo_log import log

from poppy.common import util
from poppy.manager import base
from poppy.model import ssl_certificate
from poppy.notification.mailgun import driver as n_driver
from poppy.provider.akamai.background_jobs.check_cert_status_and_update \
    import check_cert_status_and_update_flow
from poppy.provider.akamai.background_jobs.delete_policy \
    import delete_obsolete_http_policy_flow
from poppy.provider.akamai.background_jobs.update_property import \
    update_property_flow
from poppy.provider.akamai import driver as a_driver

LOG = log.getLogger(__name__)


class BackgroundJobController(base.BackgroundJobController):

    def __init__(self, manager):
        super(BackgroundJobController, self).__init__(manager)
        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller)
        self.akamai_san_cert_suffix = self.driver.conf[
            a_driver.AKAMAI_GROUP].akamai_https_access_url_suffix
        self.akamai_san_cert_cname_list = self.driver.conf[
            a_driver.AKAMAI_GROUP].san_cert_cnames
        self.akamai_sni_cert_cname_list = self.driver.conf[
            a_driver.AKAMAI_GROUP].sni_cert_cnames
        self.notify_email_list = self.driver.conf[
            n_driver.MAIL_NOTIFICATION_GROUP].recipients
        self.cert_storage = self._driver.storage.certificates_controller
        self.service_storage = self._driver.storage.services_controller

    def post_job(self, job_type, kwargs):
        queue_data = []

        run_list = []
        ignore_list = []
        if job_type == "akamai_check_and_update_cert_status":
            # this task consumes the san mapping queue
            # items marked as having an updated property are processed
            # for the this job type, all other items are returned to the
            # queue until they are ready for processing
            if 'akamai' in self._driver.providers:
                akamai_driver = self._driver.providers['akamai'].obj
                queue_data += akamai_driver.san_mapping_queue.traverse_queue(
                    consume=True
                )

                for cert in queue_data:
                    cert_dict = dict()
                    try:
                        cert_dict = json.loads(cert)
                        LOG.info(
                            'Starting to check status on domain: {0},'
                            'for project_id: {1}'
                            'flavor_id: {2}, cert_type: {3}'.format(
                                cert_dict.get("domain_name"),
                                cert_dict.get("project_id"),
                                cert_dict.get("flavor_id"),
                                cert_dict.get("cert_type")
                            )
                        )
                        t_kwargs = {
                            "cert_obj_json": json.dumps(cert_dict),
                            "project_id": cert_dict.get("project_id")
                        }
                        if cert_dict.get('property_activated', False) is True:
                            self.distributed_task_controller.submit_task(
                                check_cert_status_and_update_flow.
                                check_cert_status_and_update_flow,
                                **t_kwargs
                            )
                            run_list.append(cert_dict)
                        else:
                            akamai_driver.san_mapping_queue.\
                                enqueue_san_mapping(json.dumps(cert_dict))
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Queue item for {0} was sent back to the "
                                "queue because it wasn't marked as "
                                "activated.".format(
                                    cert_dict.get("domain_name")
                                )
                            )
                    except Exception as exc:
                        try:
                            akamai_driver.san_mapping_queue.\
                                enqueue_san_mapping(json.dumps(cert_dict))
                        except Exception as e:
                            LOG.exception(e)
                            akamai_driver.san_mapping_queue.\
                                enqueue_san_mapping(cert_dict)

                        cert_dict['error_message'] = str(exc)
                        ignore_list.append(cert_dict)
                        LOG.exception(exc)

            return run_list, ignore_list
        elif job_type == "akamai_update_papi_property_for_mod_san":
            # this task leaves the san mapping queue intact,
            # once items are successfully processed they are marked
            # ready for the next job type execution
            if 'akamai' in self._driver.providers:
                akamai_driver = self._driver.providers['akamai'].obj
                queue_data += akamai_driver.san_mapping_queue.traverse_queue()

            cname_host_info_list = []

            for cert in queue_data:
                cert_dict = dict()
                try:
                    cert_dict = json.loads(cert)
                    if cert_dict['cert_type'] == 'san':
                        # add validation that the domain still exists on a
                        # service and that it has a type of SAN
                        cert_obj = ssl_certificate.SSLCertificate(
                            cert_dict['flavor_id'],
                            cert_dict['domain_name'],
                            cert_dict['cert_type'],
                            project_id=cert_dict['project_id']
                        )

                        cert_for_domain = self.cert_storage.\
                            get_certs_by_domain(
                                cert_obj.domain_name,
                                project_id=cert_obj.project_id,
                                flavor_id=cert_obj.flavor_id,
                                cert_type=cert_obj.cert_type
                            )
                        if cert_for_domain == []:
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored property update because "
                                "certificate for {0} does not exist.".format(
                                    cert_obj.domain_name
                                )
                            )
                            continue

                        service_obj = self.service_storage.\
                            get_service_details_by_domain_name(
                                cert_obj.domain_name,
                                cert_obj.project_id
                            )
                        if service_obj is None:
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored property update because "
                                "Service not found for domain {0}".format(
                                    cert_obj.domain_name
                                )
                            )
                            continue

                        found = False
                        for domain in service_obj.domains:
                            if (
                                domain.domain == cert_obj.domain_name and
                                domain.protocol == 'https' and
                                domain.certificate == 'san'
                            ):
                                found = True
                        if found is False:
                            # skip the task for current cert obj is the
                            # domain doesn't exist on a service with the
                            # same protocol and certificate.
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored update property for domain "
                                "'{0}' that no longer exists on a service "
                                "with the same protocol 'https' and "
                                "certificate type '{1}'".format(
                                    cert_obj.domain_name,
                                    cert_obj.cert_type
                                )
                            )
                            continue
                        domain_name = cert_dict["domain_name"]
                        san_cert = (
                            cert_dict["cert_details"]
                            ["Akamai"]["extra_info"]["san cert"]
                        )
                        LOG.info(
                            "{0}: {1} to {2}, on property: {3}".format(
                                kwargs.get("action", 'add'),
                                domain_name,
                                san_cert,
                                kwargs.get(
                                    "property_spec",
                                    'akamai_https_san_config_numbers'
                                )
                            )
                        )

                        # Note(tonytan4ever): Put this check here so erroneous
                        # san cert params will not pass. Support occasionally
                        # put in the ending "edgekey.net"
                        # (e.g: securexxx.san1.abc.com.edgekey.net), this check
                        # will effectively error that out
                        if san_cert not in self.akamai_san_cert_cname_list:
                            raise ValueError(
                                "Not A valid san cert cname: {0}, "
                                "valid san cert cnames are: {1}".format(
                                    san_cert,
                                    self.akamai_san_cert_cname_list
                                )
                            )
                        cname_host_info_list.append({
                            "cnameFrom": domain_name,
                            "cnameTo": '.'.join(
                                [san_cert, self.akamai_san_cert_suffix]
                            ),
                            "cnameType": "EDGE_HOSTNAME"
                        })
                        run_list.append(cert_dict)
                except Exception as e:
                    cert_dict['error_message'] = str(e)
                    ignore_list.append(cert_dict)
                    LOG.exception(e)

            update_info_list = json.dumps([
                (
                    kwargs.get("action", 'add'),
                    cname_host_info_list
                )
            ])

            t_kwargs = {
                "property_spec": kwargs.get(
                    "property_spec",
                    'akamai_https_san_config_numbers'
                ),
                "update_type": kwargs.get("update_type", 'hostnames'),
                "update_info_list": update_info_list,
                "notify_email_list": self.notify_email_list
            }

            # check to see if there are changes to be made before submitting
            # the task, avoids creating a new property version when there are
            # no changes to be made.
            if len(cname_host_info_list) > 0:
                self.distributed_task_controller.submit_task(
                    update_property_flow.update_property_flow,
                    **t_kwargs)
            else:
                LOG.info(
                    "No tasks submitted to update_property_flow"
                    "update_info_list was empty: {0}".format(
                        update_info_list
                    )
                )

            return run_list, ignore_list
        elif job_type == 'akamai_update_papi_property_for_mod_sni':
            # this task leaves the san mapping queue intact,
            # once items are successfully processed they are marked as
            # ready for the next job type execution
            if 'akamai' in self._driver.providers:
                akamai_driver = self._driver.providers['akamai'].obj
                queue_data += akamai_driver.san_mapping_queue.traverse_queue()

            cname_host_info_list = []

            for cert in queue_data:
                cert_dict = dict()
                try:
                    cert_dict = json.loads(cert)
                    if cert_dict['cert_type'] == 'sni':
                        # validate that the domain still exists on a
                        # service and that it has a type of SAN
                        cert_obj = ssl_certificate.SSLCertificate(
                            cert_dict['flavor_id'],
                            cert_dict['domain_name'],
                            cert_dict['cert_type'],
                            project_id=cert_dict['project_id']
                        )

                        cert_for_domain = self.cert_storage.\
                            get_certs_by_domain(
                                cert_obj.domain_name,
                                project_id=cert_obj.project_id,
                                flavor_id=cert_obj.flavor_id,
                                cert_type=cert_obj.cert_type
                            )
                        if cert_for_domain == []:
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored property update because "
                                "certificate for {0} does not exist.".format(
                                    cert_obj.domain_name
                                )
                            )
                            continue

                        service_obj = self.service_storage.\
                            get_service_details_by_domain_name(
                                cert_obj.domain_name,
                                cert_obj.project_id
                            )
                        if service_obj is None:
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored property update because "
                                "Service not found for domain {0}".format(
                                    cert_obj.domain_name
                                )
                            )
                            continue

                        found = False
                        for domain in service_obj.domains:
                            if (
                                domain.domain == cert_obj.domain_name and
                                domain.protocol == 'https' and
                                domain.certificate == cert_obj.cert_type
                            ):
                                found = True
                        if found is False:
                            # skip the task for current cert obj is the
                            # domain doesn't exist on a service with the
                            # same protocol and certificate.
                            ignore_list.append(cert_dict)
                            LOG.info(
                                "Ignored update property for domain "
                                "'{0}' that no longer exists on a service "
                                "with the same protocol 'https' and  "
                                "certificate type '{1}'".format(
                                    cert_obj.domain_name,
                                    cert_obj.cert_type
                                )
                            )
                            continue
                        domain_name = cert_dict["domain_name"]
                        sni_cert = (
                            cert_dict["cert_details"]
                            ["Akamai"]["extra_info"]["sni_cert"]
                        )
                        LOG.info(
                            "{0}: {1} to {2}, on property: {3}".format(
                                kwargs.get("action", 'add'),
                                domain_name,
                                sni_cert,
                                kwargs.get(
                                    "property_spec",
                                    'akamai_https_sni_config_numbers'
                                )
                            )
                        )

                        if sni_cert not in self.akamai_sni_cert_cname_list:
                            raise ValueError(
                                "Not a valid sni cert cname: {0}, "
                                "valid sni cert cnames are: {1}".format(
                                    sni_cert,
                                    self.akamai_sni_cert_cname_list
                                )
                            )
                        cname_host_info_list.append({
                            "cnameFrom": domain_name,
                            "cnameTo": '.'.join(
                                [sni_cert, self.akamai_san_cert_suffix]
                            ),
                            "cnameType": "EDGE_HOSTNAME"
                        })
                        run_list.append(cert_dict)
                except Exception as e:
                    cert_dict['error_message'] = str(e)
                    ignore_list.append(cert_dict)
                    LOG.exception(e)

            update_info_list = json.dumps([
                (
                    kwargs.get("action", 'add'),
                    cname_host_info_list
                )
            ])

            t_kwargs = {
                "property_spec": kwargs.get(
                    "property_spec",
                    'akamai_https_sni_config_numbers'
                ),
                "update_type": kwargs.get("update_type", 'hostnames'),
                "update_info_list": update_info_list,
                "notify_email_list": self.notify_email_list
            }

            # check to see if there are changes to be made before submitting
            # the task, avoids creating a new property version when there are
            # no changes to be made.
            if len(cname_host_info_list) > 0:
                self.distributed_task_controller.submit_task(
                    update_property_flow.update_property_flow,
                    **t_kwargs)
            else:
                LOG.info(
                    "No tasks submitted to update_property_flow"
                    "update_info_list was empty: {0}".format(
                        update_info_list
                    )
                )

            return run_list, ignore_list
        else:
            raise NotImplementedError(
                'job type: {0} has not been implemented'.format(
                    job_type
                )
            )

    def get_san_mapping_list(self):
        res = []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            res = akamai_driver.san_mapping_queue.traverse_queue()
        # other provider's san_mapping_list implementation goes here

        res = [json.loads(r) for r in res]
        return res

    def put_san_mapping_list(self, san_mapping_list):
        new_queue_data = [json.dumps(r) for r in san_mapping_list]
        res, deleted = [], []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            orig = [
                json.loads(r) for r in
                akamai_driver.san_mapping_queue.traverse_queue()
            ]
            res = [
                json.loads(r) for r in
                akamai_driver.san_mapping_queue.put_queue_data(new_queue_data)
            ]

            deleted = tuple(x for x in orig if x not in res)
        # other provider's san_mapping_list implementation goes here
        return res, deleted

    def delete_http_policy(self):
        http_policies = []
        run_list = []
        ignore_list = []
        if 'akamai' in self._driver.providers:
            akamai_driver = self._driver.providers['akamai'].obj
            http_policies += akamai_driver.http_policy_queue.traverse_queue(
                consume=True
            )
            http_policies = [json.loads(x) for x in http_policies]
            http_policies = util.remove_duplicates(http_policies)

            for policy_dict in http_policies:
                cert_for_domain = self.cert_storage.get_certs_by_domain(
                    policy_dict['policy_name'],
                    project_id=policy_dict['project_id'],
                    cert_type='san'
                )
                if cert_for_domain == []:
                    ignore_list.append(policy_dict)
                    LOG.info(
                        "No cert found for policy name. "
                        "Policy {0} won't persist on the queue. ".format(
                            policy_dict
                        )
                    )
                    continue

                if cert_for_domain.get_cert_status() != 'deployed':
                    ignore_list.append(policy_dict)
                    LOG.info(
                        "Policy {0} is not ready for deletion. "
                        "Certificate exists but hasn't deployed yet. "
                        "Sending back to queue for later retry.".format(
                            policy_dict
                        )
                    )
                    akamai_driver.http_policy_queue.enqueue_http_policy(
                        json.dumps(policy_dict)
                    )
                    continue

                kwargs = {
                    'configuration_number': policy_dict[
                        'configuration_number'],
                    'policy_name': policy_dict['policy_name']
                }
                self.distributed_task_controller.submit_task(
                    delete_obsolete_http_policy_flow.
                    delete_obsolete_http_policy,
                    **kwargs
                )
                run_list.append(policy_dict)

        return run_list, ignore_list
