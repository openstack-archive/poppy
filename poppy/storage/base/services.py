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

import abc
import json

import six

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model import service
from poppy.storage.base import controller


@six.add_metaclass(abc.ABCMeta)
class ServicesControllerBase(controller.StorageControllerBase):

    def __init__(self, driver):
        super(ServicesControllerBase, self).__init__(driver)

    @abc.abstractmethod
    def list(self, project_id, marker=None, limit=None):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, project_id, service_name, service_json):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, project_id, service_name, service_json):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, project_id, service_name):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_provider_details(self, project_id, service_name):
        raise NotImplementedError

    @abc.abstractmethod
    def update_provider_details(self, provider_details):
        raise NotImplementedError

    @staticmethod
    def format_result(result):
        name = result.get('service_name')
        origins = [json.loads(o) for o in result.get('origins', [])]
        domains = [json.loads(d) for d in result.get('domains', [])]
        origins = [origin.Origin(o['origin'],
                                 o.get('port', 80),
                                 o.get('ssl', False))
                   for o in origins]
        domains = [domain.Domain(d['domain']) for d in domains]
        flavorRef = result.get('flavorRef')
        s = service.Service(name, domains, origins, flavorRef)
        provider_detail_results = result.get('provider_details')
        provider_details_dict = {}
        for provider_name in provider_detail_results:
            provider_detail_dict = json.loads(
                provider_detail_results[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            provider_details_dict[provider_name] = provider_detail_obj
        s.provider_details = provider_details_dict
        return s
