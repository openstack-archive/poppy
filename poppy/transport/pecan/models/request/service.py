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

from poppy.model import service
from poppy.transport.pecan.models.request import cachingrule
from poppy.transport.pecan.models.request import domain
from poppy.transport.pecan.models.request import origin
from poppy.transport.pecan.models.request import restriction


def load_from_json(json_data):
    name = json_data.get("name")
    origins = json_data.get("origins", [])
    domains = json_data.get("domains", [])
    flavor_ref = json_data.get("flavor_ref")
    restrictions = json_data.get("restrictions", [])
    caching = json_data.get("caching", [])
    origins = [origin.load_from_json(o) for o in origins]
    domains = [domain.load_from_json(d) for d in domains]
    restrictions = [restriction.load_from_json(r) for r in restrictions]
    caching = [cachingrule.load_from_json(c) for c in caching]
    res = service.Service(name, domains, origins, flavor_ref)
    res.caching = caching
    res.restrictions = restrictions
    return res
