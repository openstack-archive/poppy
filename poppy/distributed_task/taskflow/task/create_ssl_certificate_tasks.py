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
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.openstack.common import log
from poppy.transport.pecan.models.request import ssl_certificate

LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class CreateProviderSSLCertificateTask(task.Task):
    default_provides = "responders"

    def execute(self, providers_list_json, cert_obj_json):
        service_controller, ssl_certificate_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        # call provider create_ssl_certificate function
        providers_list = json.loads(providers_list_json)
        cert_obj = ssl_certificate.load_from_json(json.loads(cert_obj_json))

        responders = []
        # try to create all service from each provider
        for provider in providers_list:
            LOG.info('Starting to create ssl certificate: {0}'.format(
                cert_obj.to_dict()))
            LOG.info('from {0}'.format(provider))
            responder = service_controller.provider_wrapper.create_certificate(
                service_controller._driver.providers[provider],
                cert_obj
            )
            responders.append(responder)

        return responders


class SendNotificationTask(task.Task):

    def execute(self, responders):
        service_controller, ssl_certificate_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        notification_content = ""
        for responder in responders:
            for provider in responder:
                notification_content += (
                    "Provider: %s, Detail: %s" %
                    (provider, str(responder[provider])))

        for n_driver in service_controller._driver.notification:
            service_controller.notification_wrapper.send(
                n_driver,
                n_driver.notification_subject,
                notification_content)

        return
