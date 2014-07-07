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

"""CDN Provider implementation."""

from cdn.common import decorators
from cdn.openstack.common import log as logging
from cdn import provider
from cdn.provider.mock import controllers

LOG = logging.getLogger(__name__)


class CDNProvider(provider.CDNProviderBase):

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

    def is_alive(self):
        return True

    @decorators.lazy_property(write=False)
    def service_controller(self):
        return controllers.ServiceController()
