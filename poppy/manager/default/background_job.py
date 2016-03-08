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

from oslo_config import cfg
from oslo_log import log

from poppy.manager import base
from poppy.notification.mailgun import driver as n_driver
from poppy.provider.akamai.background_jobs.check_cert_status_and_update import \
    check_cert_status_and_update_flow
from poppy.provider.akamai.background_jobs.update_property import \
    update_property_flow
from poppy.provider.akamai import driver as a_driver

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])
LOG = log.getLogger(__name__)


class BackgroundJobController(base.BackgroundJobController):

    def __init__(self, manager):
        super(BackgroundJobController, self).__init__(manager)
        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller)
        self.akamai_san_cert_suffix = (
            conf[a_driver.AKAMAI_GROUP].akamai_https_access_url_suffix)
        self.akamai_san_cert_cname_list = (
            conf[a_driver.AKAMAI_GROUP].san_cert_cnames)
        self.notify_email_list = (
            conf[n_driver.MAIL_NOTIFICATION_GROUP].recipients)

    def post_job(self, job_type, kwargs):
        kwargs = kwargs
        if job_type == "akamai_check_and_update_cert_status":
            LOG.info('Starting to check status on domain: {0},'
                     'for project_id: {1}'
                     'flavor_id: {2}, cert_type: {3}'.format(
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
            LOG.info('{0}: {1} to {2}, on property: {3}'.format(
                kwargs.get("action", 'add'),
                kwargs.get("domain_name"),
                kwargs.get("san_cert_name"),
                kwargs.get("property_spec", 'akamai_https_san_config_numbers')
            ))

            # Note(tonytan4ever): Put this check here so erroneous
            # san cert params will not pass. Support occassionally put in
            # the ending "edgekey.net"
            # (e.g: securexxx.san1.abc.com.edgekey.net), this check will
            # effectively error that out
            if kwargs.get("san_cert_name") not in \
                    self.akamai_san_cert_cname_list:
                raise ValueError('Not A valid san cert cname: {0}, '
                                 'valid san cert cnames are: {1}'.format(
                                     kwargs.get("san_cert_name"),
                                     self.akamai_san_cert_cname_list))

            t_kwargs = {}

            update_info_list = json.dumps([
                (kwargs.get("property_spec", 'add'),
                    {
                        "cnameFrom": kwargs.get("domain_name"),
                        "cnameTo": '.'.join([kwargs.get("san_cert_name"),
                                             kwargs.get(
                                            "san_cert_domain_suffix",
                                            self.akamai_san_cert_suffix)]),
                        "cnameType": "EDGE_HOSTNAME"
                    })
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
            raise NotImplementedError(
                'job type: {0} has not been implemented').format(
                job_type)
