# Copyright (c) 2016 Rackspace, Inc.
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

from oslo_config import cfg
from oslo_log import log
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers

LOG = log.getLogger(__name__)

conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class DeleteObsoleteHTTPPolicy(task.Task):
    """Delete old HTTP policy once a domain is upgraded to HTTPS SAN."""

    def __init__(self):
        super(DeleteObsoleteHTTPPolicy, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj

    def execute(self, configuration_number, policy_name):
        """Deletes old HTTP policy once a domain is upgraded to HTTPS+san.

        :param configuration_number: akamai configuration number
        :param policy_name: name of policy on akamai policy api
        """

        resp = self.akamai_driver.policy_api_client.delete(
            self.akamai_driver.akamai_policy_api_base_url.format(
                configuration_number=configuration_number,
                policy_name=policy_name
            )
        )
        LOG.info(
            'akamai response code: {0}'.format(resp.status_code))
        LOG.info('akamai response text: {0}'.format(resp.text))
        if resp.status_code != 200:
            raise RuntimeError(resp.text)
        LOG.info(
            'Delete old policy {0} complete'.format(policy_name))
