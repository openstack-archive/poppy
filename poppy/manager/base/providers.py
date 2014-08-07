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


class ProviderWrapper(object):
    def create(self, ext, service_name, service_json):
        return ext.obj.service_controller.create(service_name, service_json)

    def update(self, ext, service_name, service_json):
        return ext.obj.service_controller.update(service_name, service_json)

    def delete(self, ext, service_name):
        return ext.obj.service_controller.delete(service_name)
