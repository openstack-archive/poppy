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

from oslo.config import cfg

from poppy import bootstrap
from poppy.manager.delegate import service_queue_workers
from poppy.transport.pecan.models.request import service
from poppy.openstack.common import log


LOG = log.getLogger(__name__)


def manager_daemon(queue):
    LOG.info('Starting running Poppy delegate manager daemon...')
    conf = cfg.CONF
    conf(project='poppy', prog='poppy', args=[])
    mgr = bootstrap.Bootstrap(conf).manager
    while True:
        message_body = queue.dequeue()
        message = json.loads(message_body)
        project_id = message['project_id']
        service_json = message['body']
        service_name = service_json['name']
        service_obj = service.load_from_json(service_json)
        if message['action'] == 'create':
            LOG.info('Starting to create service %s for %s' %
                     (service_name, project_id))
            service_queue_workers.create_service_worker(mgr, project_id,
                                                        service_name,
                                                        service_obj)
        else:
            LOG.info('Other actions (update/delete) does not have'
                     'worker implmented yet...')
