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
from poppy.transport.pecan.models.request import log_delivery as ld
from poppy.transport.pecan.models.request import origin
from poppy.transport.pecan.models.request import provider_details
from poppy.transport.pecan.models.request import restriction


def load_from_json(json_data):
    service_id = json_data.get('service_id', uuid.uuid4())

    name = json_data.get("name")
    origins = json_data.get("origins", [])
    domains = json_data.get("domains", [])
    flavor_id = json_data.get("flavor_id")
    restrictions = json_data.get("restrictions", [])
    project_id = json_data.get("project_id")
    pd = json_data.get("provider_details", {})
    log_delivery = json_data.get("log_delivery", {})

    # load caching rules json string from input
    origins = [origin.load_from_json(o) for o in origins]
    domains = [domain.load_from_json(d) for d in domains]
    restrictions = [restriction.load_from_json(r) for r in restrictions]
    log_delivery = ld.load_from_json(log_delivery)

    # convert caching rule json string list into object list
    caching = json_data.get("caching", [])
    caching = [cachingrule.load_from_json(c) for c in caching]

    r = service.Service(service_id=service_id,
                        name=name,
                        domains=domains,
                        origins=origins,
                        flavor_id=flavor_id,
                        caching=caching,
                        restrictions=restrictions,
                        log_delivery=log_delivery,
                        project_id=project_id)

    r.provider_details = dict([(k, provider_details.load_from_json(v))
                               for k, v in pd.items()])
    return r
