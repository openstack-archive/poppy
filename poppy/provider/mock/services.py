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
import random

from poppy.openstack.common import log
from poppy.provider import base

LOG = log.getLogger(__name__)


class ServiceController(base.ServiceBase):

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

    def update(self, provider_detail, service_json):
        provider_detail_dict = json.loads(provider_detail)
        service_id = provider_detail_dict['id']
        return self.responder.updated(service_id)

    def create(self, service_name, service_json):
        LOG.debug("Mock creating service: %s" % service_name)
        # We generate a fack id here
        service_id = random.randint(1, 10000)
        return self.responder.created(service_id)

    def delete(self, provider_detail):
        provider_detail_dict = json.loads(provider_detail)
        service_id = provider_detail_dict['id']
        return self.responder.deleted(service_id)
