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

from poppy.common import errors


class ProviderWrapper(object):

    def health(self, ext):
        return {'provider_name': ext.obj.provider_name,
                'health': ext.obj.is_alive()}

    def create(self, ext, service_name, service_json):
        return ext.obj.service_controller.create(service_name, service_json)

    def update(self, ext, provider_details, service_json):
        try:
            provider_detail = provider_details[ext.provider_name]
        except KeyError:
            raise errors.BadProviderDetail(
                "No provider detail information."
                "Perhaps service has not been created")
        provider_service_id = provider_detail.id
        return ext.obj.service_controller.update(
            provider_service_id,
            service_json)

    def delete(self, ext, provider_details):
        try:
            provider_detail = provider_details[ext.provider_name]
        except KeyError:
            raise errors.BadProviderDetail(
                "No provider detail information."
                "Perhaps service has not been created")
        provider_service_id = provider_detail.id
        return ext.obj.service_controller.delete(provider_service_id)
