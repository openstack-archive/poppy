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

    def __init__(self, name=None, domain_list=None, origin_list=None,
                 flavorRef=None, caching_list=None):
        super(CreateService, self).__init__()

        self.service_name = name
        self.domain_list = domain_list or []
        self.origin_list = origin_list or []
        self.flavorRef = flavorRef
        self.caching_list = caching_list or []

    def _obj_to_json(self):
        create_service_request = {"name": self.service_name,
                                  "domains": self.domain_list,
                                  "origins": self.origin_list,
                                  "flavorRef": self.flavorRef,
                                  "caching": self.caching_list}
        return json.dumps(create_service_request)
