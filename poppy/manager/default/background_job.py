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

from poppy.manager import base
from poppy.notification.mailgun import driver as n_driver
from poppy.openstack.common import log
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
        self.notify_email_list = (
            conf[n_driver.MAIL_NOTIFICATION_GROUP].recipients)

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
            LOG.info("%s: %s to %s, on property: %s" % (
                kwargs.get("action", 'add'),
                kwargs.get("domain_name"),
                kwargs.get("san_cert_name"),
                kwargs.get("property_spec", 'akamai_https_san_config_numbers')
            ))

            t_kwargs = {}

            update_info_list = json.dumps([
                (kwargs.get("property_spec", 'add'),
                    {
                        "cnameFrome": kwargs.get("domain_name"),
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
            raise NotImplementedError('job type: %s has not been implemented')
