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
from cdn.storage import base


class ServicesController(base.ServicesController):

    def list(self, project_id):
        services = {}
        return services

    def get(self, project_id, service_name):
        # get the requested service from storage
        pass

    def create(self, project_id, service_name, service_json):

        # create the service in storage
        pass

    def update(self, project_id, service_name, service_json):
        # update configuration in storage
        pass

    def delete(self, project_id, service_name):
        # delete local configuration from storage
        pass
