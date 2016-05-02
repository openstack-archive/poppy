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

from poppy.manager import base
from poppy.notification.mailgun import driver as n_driver
from poppy.provider.akamai.background_jobs.check_cert_status_and_update \
    import check_cert_status_and_update_flow
from poppy.provider.akamai.background_jobs.update_property import \
    update_property_flow
from poppy.provider.akamai import driver as a_driver

LOG = log.getLogger(__name__)


class BackgroundJobController(base.BackgroundJobController):

    def __init__(self, manager):
        super(BackgroundJobController, self).__init__(manager)
        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller
        )
        self.akamai_san_cert_suffix = self.driver.conf[
            a_driver.AKAMAI_GROUP].akamai_https_access_url_suffix

        self.akamai_san_cert_cname_list = self.driver.conf[
            a_driver.AKAMAI_GROUP].san_cert_cnames

        self.notify_email_list = self.driver.conf[
            n_driver.MAIL_NOTIFICATION_GROUP].recipients

    def post_job(self, job_type, kwargs):
        kwargs = kwargs
        if job_type == "akamai_check_and_update_cert_status":
            LOG.info('Starting to check status on domain: %s,'
                     'for project_id: %s'
                     'flavor_id: %s, cert_type: %s' %
                     (
                         kwargs.get("domain_name"),
                         kwargs.get("project_id"),
                         kwargs.get("flavor_id"),
                         kwargs.get("cert_type")
                     ))
            self.distributed_task_controller.submit_task(
                check_cert_status_and_update_flow.
                check_cert_status_and_update_flow,
                **kwargs)
        elif job_type == "akamai_update_papi_property_for_mod_san":
            update_cname_host_mapping_info = kwargs.get(
                "update_cname_host_mapping_info"
            )

            cname_host_info_list = []
            for domain_san_cert_cname_pair in update_cname_host_mapping_info:
                LOG.info("%s: %s to %s, on property: %s" % (
                    kwargs.get("action", 'add'),
                    domain_san_cert_cname_pair["domain_name"],
                    domain_san_cert_cname_pair["san_cert_name"],
                    kwargs.get("property_spec",
                               'akamai_https_san_config_numbers')
                ))

                # Note(tonytan4ever): Put this check here so erroneous
                # san cert params will not pass. Support occasionally put in
                # the ending "edgekey.net"
                # (e.g: securexxx.san1.abc.com.edgekey.net), this check will
                # effectively error that out
                if domain_san_cert_cname_pair["san_cert_name"] not in \
                        self.akamai_san_cert_cname_list:
                    raise ValueError("Not A valid san cert cname: %s, "
                                     "valid san cert cnames are: %s" %
                                     (kwargs.get("san_cert_name"),
                                      self.akamai_san_cert_cname_list))
                cname_host_info_list.append({
                    "cnameFrom": domain_san_cert_cname_pair["domain_name"],
                    "cnameTo": '.'.join([domain_san_cert_cname_pair[
                                         "san_cert_name"],
                                         kwargs.get("san_cert_domain_suffix",
                                         self.akamai_san_cert_suffix)]),
                    "cnameType": "EDGE_HOSTNAME"
                })

            t_kwargs = {}

            update_info_list = json.dumps([
                (kwargs.get("action", 'add'),
                    cname_host_info_list)
            ])

            t_kwargs = {
                "property_spec": kwargs.get("property_spec",
                                            'akamai_https_san_config_numbers'),
                "update_type": kwargs.get("update_type", 'hostnames'),
                "update_info_list": update_info_list,
                "notify_email_list": self.notify_email_list
            }

            self.distributed_task_controller.submit_task(
                update_property_flow.update_property_flow,
                **t_kwargs)
        else:
            raise NotImplementedError('job type: %s has not been implemented')

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
