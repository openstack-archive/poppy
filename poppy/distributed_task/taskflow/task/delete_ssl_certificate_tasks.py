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


class DeleteProviderSSLCertificateTask(task.Task):
    default_provides = "responders"

    def execute(self, providers_list_json, cert_obj_json):
        service_controller = memoized_controllers.task_controllers('poppy')

        cert_obj = ssl_certificate.load_from_json(json.loads(cert_obj_json))
        providers_list = json.loads(providers_list_json)

        responders = []
        # try to delete all certificates from each provider
        for provider in providers_list:
            LOG.info(
                'Starting to delete ssl certificate: {0} from {1}.'.format(
                    cert_obj.to_dict(), provider))
            responder = service_controller.provider_wrapper.delete_certificate(
                service_controller._driver.providers[provider],
                cert_obj,
            )
            responders.append(responder)

        return responders


class SendNotificationTask(task.Task):

    def execute(self, project_id, responders, domain_name, cert_type):
        service_controller = memoized_controllers.task_controllers('poppy')

        notification_content = (
            "Project ID: %s, Domain Name: %s, Cert type: %s" %
            (project_id, domain_name, cert_type))

        notification_content = ""
        for responder in responders:
            for provider in responder:
                notification_content += (
                    "Project ID: {0}, Provider: {1}, "
                    "Detail: {2}, Cert type: {3}".format(
                        project_id,
                        provider,
                        str(responder[provider]),
                        cert_type
                    )
                )

        for n_driver in service_controller._driver.notification:
            service_controller.notification_wrapper.send(
                n_driver,
                "Poppy Certificate Deleted",
                notification_content)

        return


class DeleteStorageSSLCertificateTask(task.Task):

    def execute(self, project_id, domain_name, cert_type):
        service_controller, self.ssl_certificate_manager = \
            memoized_controllers.task_controllers('poppy', 'ssl_certificate')
        self.storage_controller = self.ssl_certificate_manager.storage

        try:
            self.storage_controller.delete_certificate(
                project_id,
                domain_name,
                cert_type
            )
        except ValueError as e:
            LOG.exception(e)

    def revert(self, *args, **kwargs):
        try:
            if getattr(self, 'storage_controller') \
                    and self.storage_controller._driver.session:
                self.storage_controller._driver.close_connection()
                LOG.info('Cassandra session being shutdown')
        except AttributeError:
            LOG.info('Cassandra session already shutdown')
