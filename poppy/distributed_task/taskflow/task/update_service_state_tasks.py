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
import time

from oslo_config import cfg
from oslo_log import log
from taskflow import task

from poppy.distributed_task.utils import exc_loader
from poppy.distributed_task.utils import memoized_controllers
from poppy.transport.pecan.models.request import service


LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])

DNS_OPTIONS = [
    cfg.IntOpt('retries', default=5,
               help='Total number of Retries after Exponentially Backing Off')
]

DNS_GROUP = 'driver:dns'

conf.register_opts(DNS_OPTIONS, group=DNS_GROUP)


class UpdateServiceStateTask(task.Task):
    def execute(self, project_id, service_obj, state):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, self.storage_controller = \
            memoized_controllers.task_controllers('poppy', 'storage')

        LOG.info(u'Starting to update service state to %s, for '
                 'project_id: %s, service_id: %s'
                 % (state, project_id, service_obj.service_id))
        self.storage_controller.update_state(
            project_id, service_obj.service_id, state)
        LOG.info(u'Update service state complete.')


class FixDNSChainTask(task.Task):
    def execute(self, service_obj, project_id, retry_sleep_time):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        LOG.info(u'Starting to enable service - '
                 u'service_id: {0}, '
                 u'project_id: {1}'.format(service_obj.service_id,
                                           project_id))
        dns_responder = dns.enable(service_obj)

        for provider_name in dns_responder:
            try:
                if 'error' in dns_responder[provider_name]:
                    msg = 'Fixing DNS Chain for {0} ' \
                          'failed!'.format(provider_name)
                    LOG.info(msg)
                    if 'error_class' in dns_responder[provider_name]:
                        exception_repr = \
                            dns_responder[provider_name]['error_class']
                        exception_class = exc_loader(exception_repr)

                        if any([exception_class == exception for
                                exception in dns._driver.retry_exceptions]):
                            LOG.info('Due to {0} Exception, '
                                     'Task {1} will '
                                     'be retried'.format(exception_class,
                                                         self.__class__))
                            raise exception_class(msg)
                else:
                    LOG.info("Fixing DNS Chain Successful "
                             "for Provider {0} : "
                             "{1}".format(provider_name,
                                          dns_responder[provider_name]))
            except KeyError:
                # NOTE(TheSriram): This means the provider updates failed, and
                # just access_urls were returned
                pass

        LOG.info(u'Enabled service - '
                 u'service_id: {0}, '
                 u'project_id: {1}'.format(service_obj.service_id,
                                           project_id))

    def revert(self, service_obj, project_id, retry_sleep_time, **kwargs):
        if self.name in kwargs['flow_failures'].keys():
            retries = conf[DNS_GROUP].retries
            current_progress = (1.0 / retries)
            if hasattr(self, 'retry_progress') \
                    and hasattr(self, 'retry_index'):
                self.retry_index = self.retry_index + 1
                self.retry_progress = current_progress * self.retry_index
            if not hasattr(self, 'retry_progress') \
                    and not hasattr(self, 'retry_index'):
                self.retry_progress = current_progress
                self.retry_index = 1
            if self.retry_progress == 1.0:
                LOG.warning(
                    'Maximum retry attempts of '
                    '{0} reached for Task {1}'.format(retries, self.name))
                service_obj_json = json.loads(service_obj)
                service_obj = service.load_from_json(service_obj_json)
                LOG.warning(
                    'DNS enabling on service_id: '
                    '{0} and project_id: {1} '
                    ' failed'.format(service_obj.service_id, project_id))
                result = kwargs['result']
                exc_class = str(result.exc_info[0])
                exc_traceback = result.traceback_str
                LOG.warning(
                    'Error Class : {0} for '
                    'service_id: {1} '
                    'and project_id: {2}'.format(exc_class,
                                                 service_obj.service_id,
                                                 project_id))
                LOG.warning(
                    'Error Traceback : {0} for '
                    'service_id: {1} '
                    'and project_id: {2}'.format(exc_traceback,
                                                 service_obj.service_id,
                                                 project_id))

            else:
                LOG.warning('Sleeping for {0} seconds and '
                            'retrying'.format(retry_sleep_time))
                if retry_sleep_time is not None:
                    time.sleep(retry_sleep_time)


class BreakDNSChainTask(task.Task):
    def execute(self, service_obj, project_id, retry_sleep_time):
        service_obj_json = json.loads(service_obj)
        service_obj = service.load_from_json(service_obj_json)

        service_controller, dns = \
            memoized_controllers.task_controllers('poppy', 'dns')

        LOG.info(u'Starting to disable service - '
                 u'service_id: {0}, '
                 u'project_id: {1}'.format(service_obj.service_id,
                                           project_id))
        dns_responder = dns.disable(service_obj)
        for provider_name in dns_responder:
            try:
                if 'error' in dns_responder[provider_name]:
                    msg = 'Breaking DNS Chain for {0} ' \
                          'failed!'.format(provider_name)
                    LOG.info(msg)
                    if 'error_class' in dns_responder[provider_name]:
                        exception_repr = \
                            dns_responder[provider_name]['error_class']
                        exception_class = exc_loader(exception_repr)

                        if any([exception_class == exception for
                                exception in dns._driver.retry_exceptions]):
                            LOG.info('Due to {0} Exception, '
                                     'Task {1} will '
                                     'be retried'.format(exception_class,
                                                         self.__class__))
                            raise exception_class(msg)
                else:
                    LOG.info("Breaking DNS Chain Successful "
                             "for Provider {0} : "
                             "{1}".format(provider_name,
                                          dns_responder[provider_name]))
            except KeyError:
                # NOTE(TheSriram): This means the provider updates failed, and
                # just access_urls were returned
                pass

        LOG.info(u'Disabled service - '
                 u'service_id: {0}, '
                 u'project_id: {1}'.format(service_obj.service_id,
                                           project_id))

        return

    def revert(self, service_obj, project_id, retry_sleep_time, **kwargs):
        if self.name in kwargs['flow_failures'].keys():
            retries = conf[DNS_GROUP].retries
            current_progress = (1.0 / retries)
            if hasattr(self, 'retry_progress') \
                    and hasattr(self, 'retry_index'):
                self.retry_index = self.retry_index + 1
                self.retry_progress = current_progress * self.retry_index
            if not hasattr(self, 'retry_progress') \
                    and not hasattr(self, 'retry_index'):
                self.retry_progress = current_progress
                self.retry_index = 1
            if self.retry_progress == 1.0:
                LOG.warning(
                    'Maximum retry attempts of '
                    '{0} reached for Task {1}'.format(retries, self.name))
                service_obj_json = json.loads(service_obj)
                service_obj = service.load_from_json(service_obj_json)
                LOG.warning(
                    'DNS enabling on service_id: '
                    '{0} and project_id: {1} '
                    ' failed'.format(service_obj.service_id, project_id))
                result = kwargs['result']
                exc_class = str(result.exc_info[0])
                exc_traceback = result.traceback_str
                LOG.warning(
                    'Error Class : {0} for '
                    'service_id: {1} '
                    'and project_id: {2}'.format(exc_class,
                                                 service_obj.service_id,
                                                 project_id))
                LOG.warning(
                    'Error Traceback : {0} for '
                    'service_id: {1} '
                    'and project_id: {2}'.format(exc_traceback,
                                                 service_obj.service_id,
                                                 project_id))

            else:
                LOG.warning('Sleeping for {0} seconds and '
                            'retrying'.format(retry_sleep_time))
                if retry_sleep_time is not None:
                    time.sleep(retry_sleep_time)
