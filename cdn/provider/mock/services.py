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

# stevedore/example/simple.py
from cdn.provider import base


class ServiceController(base.ServiceBase):

    def __init__(self):
        super(ServiceController, self).__init__()

        self.provider_resp = base.ProviderResponse("mock")

    def update(self, service_name, service_json):
        return self.provider_resp.updated(service_name)

    def create(self, service_name, service_json):
        return self.provider_resp.created(service_name)

    def delete(self, service_name):
        return self.provider_resp.deleted(service_name)
