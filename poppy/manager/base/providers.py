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
    """"ProviderWrapper class."""

    def create(self, ext, service_obj):
        """Create a provider

        :param ext
        :param service_obj
        :returns: ext.obj.service_controller.create(service_obj)
        """

        return ext.obj.service_controller.create(service_obj)

    def update(self, ext, provider_details, service_obj):
        """Update a provider

        :param ext
        :param provider_details
        :param service_obj
        """

        try:
            provider_detail = provider_details[ext.obj.provider_name]
        except KeyError:
            raise errors.BadProviderDetail(
                "No provider detail information."
                "Perhaps service has not been created")
        provider_service_id = provider_detail.provider_service_id
        return ext.obj.service_controller.update(
            provider_service_id, service_obj)

    def delete(self, ext, provider_details, project_id):
        try:
            provider_detail = provider_details[ext.obj.provider_name]
        except KeyError:
            raise errors.BadProviderDetail(
                "No provider detail information."
                "Perhaps service has not been created")
        provider_service_id = provider_detail.provider_service_id
        return ext.obj.service_controller.delete(project_id,
                                                 provider_service_id)

    def purge(self, ext, service_obj, provider_details,
              hard=False, purge_url=None):
        try:
            provider_detail = provider_details[ext.obj.provider_name]
        except KeyError:
            raise errors.BadProviderDetail(
                "No provider detail information."
                "Perhaps service has not been created")
        provider_service_id = provider_detail.provider_service_id
        return ext.obj.service_controller.purge(
            provider_service_id,
            service_obj,
            hard,
            purge_url)

    def create_certificate(self, ext, cert_obj, enqueue):
        """Create a certificate

        :param ext
        :param cert_obj
        :param enqueue
        :returns: ext.obj.service_controller.create(service_obj)
        """

        return ext.obj.certificate_controller.create_certificate(
            cert_obj,
            enqueue
        )
