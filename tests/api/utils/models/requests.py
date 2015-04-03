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

from cafe.engine.models import base


class CreateService(base.AutoMarshallingModel):
    """Marshalling for Create Service requests."""

    def __init__(self, service_name=None, domain_list=None, origin_list=None,
                 caching_list=None, restrictions_list=None, flavor_id=None,
                 log_delivery=False):
        super(CreateService, self).__init__()

        self.service_name = service_name
        self.domain_list = domain_list or []
        self.origin_list = origin_list or []
        self.caching_list = caching_list or []
        self.restrictions_list = restrictions_list or []
        self.flavor_id = flavor_id
        self.log_delivery = log_delivery

    def _obj_to_json(self):
        create_service_request = {"name": self.service_name,
                                  "domains": self.domain_list,
                                  "origins": self.origin_list,
                                  "caching": self.caching_list,
                                  "restrictions": self.restrictions_list,
                                  "flavor_id": self.flavor_id,
                                  "log_delivery": self.log_delivery}
        return json.dumps(create_service_request)


class PatchService(base.AutoMarshallingModel):
    """Marshalling for Patch Service requests."""

    def __init__(self, request_body=None):
        super(PatchService, self).__init__()

        self.request_body = request_body

    def _obj_to_json(self):
        patch_service_request = self.request_body
        return json.dumps(patch_service_request)


class CreateFlavor(base.AutoMarshallingModel):
    """Marshalling for Create Flavor requests."""

    def __init__(self, flavor_id=None, provider_list=None, limits=None):
        super(CreateFlavor, self).__init__()

        self.flavor_id = flavor_id
        self.provider_list = provider_list
        self.limits = limits

    def _obj_to_json(self):
        create_flavor_request = {"id": self.flavor_id,
                                 "providers": self.provider_list,
                                 "limits": self.limits}
        return json.dumps(create_flavor_request)
