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
import uuid

from poppy.model import service
from poppy.transport.pecan.models.request import cachingrule
from poppy.transport.pecan.models.request import domain
from poppy.transport.pecan.models.request import origin
from poppy.transport.pecan.models.request import provider_details
from poppy.transport.pecan.models.request import restriction


def load_from_json(json_data):
    service_id = uuid.uuid4()

    name = json_data.get("name")
    origins = json_data.get("origins", [])
    domains = json_data.get("domains", [])
    flavor_id = json_data.get("flavor_id")
    restrictions = json_data.get("restrictions", [])
    pd = json_data.get("provider_details", {})

    # load from input
    origins = [origin.load_from_json(o) for o in origins]
    domains = [domain.load_from_json(d) for d in domains]
    restrictions = [restriction.load_from_json(r) for r in restrictions]

    # convert caching rule json string list into object list
    caching = json_data.get("caching", [])
    default_rules = [c for c in caching
                     for r in c['rules']
                     if r['request_url'] == '/*']
    if len(default_rules) == 0:
        # add a default ttl if none provided.
        default_ttl = {
            "name": "default",
            "ttl": 86400,
            "rules": [
                    {
                        "name": "default",
                        "request_url": "/*"
                    }
            ]
        }

        caching.insert(0, default_ttl)

    caching = [cachingrule.load_from_json(c) for c in caching]

    r = service.Service(service_id,
                        name,
                        domains,
                        origins,
                        flavor_id,
                        caching,
                        restrictions)

    r.provider_details = dict([(k, provider_details.load_from_json(v))
                               for k, v in pd.items()])
    return r
