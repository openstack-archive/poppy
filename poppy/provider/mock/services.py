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

import uuid

from poppy.common import decorators
from poppy.openstack.common import log
from poppy.provider import base

LOG = log.getLogger(__name__)


class ServiceController(base.ServiceBase):

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

    def update(self, provider_service_id, service_obj):
        return self.responder.updated(provider_service_id)

    def create(self, service_obj):
        # We generate a fake id here
        service_id = uuid.uuid1()
        return self.responder.created(str(service_id), [{
            "href": "www.mysite.com",
            'rel': "access_url"}])

    def delete(self, provider_service_id):
        return self.responder.deleted(provider_service_id)

    def purge(self, provider_service_id, purge_urls=None):
        return self.responder.purged(provider_service_id)

    def get(self, service_name):
        return self.responder.get([], [], [])

    @decorators.lazy_property(write=False)
    def current_customer(self):
        '''return current_customer for Mock. We can return a None.'''
        return None
