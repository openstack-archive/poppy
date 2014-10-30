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

"""Zaqar Driver implementation."""

from oslo.config import cfg
from zaqarclient.queues.v1 import client

from poppy.queue import base
from poppy.queue.zaqar import controllers
from poppy.openstack.common import log as logging


ZAQAR_OPTIONS = [
    cfg.StrOpt('project_id', default='',
               help='Keystone Project ID'),
    cfg.StrOpt('api_key', default='',
               help='Keystone API Key'),
    cfg.StrOpt('base_url', default='',
               help='The ZAQAR url'),
    cfg.StrOpt('queue_name', default='poppy_queue',
               help='The Queue Name to use'),
    cfg.IntOpt('message_ttl', default='6000',
               help='The default TTL value for posted messages'),
    cfg.IntOpt('claim_ttl', default='6000',
               help='The default TTL value for claims'),
]

ZAQAR_GROUP = 'drivers:queue:zaqar'

LOG = logging.getLogger(__name__)


class QueueDriver(base.Driver):

    def __init__(self, conf):
        super(QueueDriver, self).__init__(conf)
        self._conf.register_opts(ZAQAR_OPTIONS, group=ZAQAR_GROUP)
        self.zaqar_conf = self._conf[ZAQAR_GROUP]

        # TODO(malini): Add Auth Support. The current zaqar driver only
        # supports a zaqar driver with auth turned off(GASP!!!)
        self.zaqar_client = client.Client(self.zaqar_conf.url)
        self.queue = self.zaqar_client.queue(self.zaqar_conf.queue_name)

    def is_alive(self):
        response = self.zaqar_client.health()
        if response.status_code == 200:
            return True
        return False

    def enqueue(self, action, project_id, service_name, body):
        message_body = {
            'ttl': self.zaqar_conf.message_ttl,
            'body': {
                'action': action,
                'project_id': project_id,
                'service_name': service_name,
                'body': body}}
        resp = self.queue.post(message_body)
        return resp

    def peek(self):
        claimed = self.queue.claim(ttl=self.zaqar_conf.claim_ttl, grace=900,
                                   limit=1)
        for msg in claimed:
            return msg

    def dequeue(self, msg):
        resp = msg.delete()
        return resp

    @property
    def service_controller(self):
        return controllers.ServiceController(self)
