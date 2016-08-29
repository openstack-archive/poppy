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
from taskflow.patterns import linear_flow

from poppy.provider.akamai.background_jobs.delete_policy import (
    delete_obsolete_http_policy_tasks)

LOG = log.getLogger(__name__)


conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


def delete_obsolete_http_policy():
    flow = linear_flow.Flow('Deleting obsolete HTTP policy').add(
        delete_obsolete_http_policy_tasks.DeleteObsoleteHTTPPolicy(),
    )
    return flow
