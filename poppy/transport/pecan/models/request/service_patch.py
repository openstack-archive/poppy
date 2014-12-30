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
from poppy.transport.pecan.models.request import provider_details
from poppy.transport.pecan.models.request import restriction


def load_from_json(json_data):
    import pdb; pdb.set_trace()
    name = json_data.get("name")
    origins = json_data.get("origins", [])
    domains = json_data.get("domains", [])
    flavor_id = json_data.get("flavor_id")
    restrictions = json_data.get("restrictions", [])
    pd = json_data.get("provider_details", {})
    # load caching rules json string from input
    caching = json_data.get("caching", [])
    origins = [origin.load_from_json(o) for o in origins]
    domains = [domain.load_from_json(d) for d in domains]
    restrictions = [restriction.load_from_json(r) for r in restrictions]
    # convert caching rule jsong string list into object list
    caching = [cachingrule.load_from_json(c) for c in caching]
    r = service.Service(name, domains, origins, flavor_id, caching,
                        restrictions)
    r.provider_details = dict([(k, provider_details.load_from_json(v))
                               for k, v in pd.items()])
    return r


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

import jsonpatch


class ServicePatch(service.Service):
    def __init__(self, json):
        super(ServicePatch, self).__init__(
            name='',
            domains=[],
            origins=[],
            flavor_id=''
        )
        import pdb; pdb.set_trace()

        # patch this model against ops
        jsonpatch.apply_patch(self.to_dict(), json, in_place=True)

"""
class BackupPatchRequestModel(object):
        self.state = DEFAULT_VALUE
        self.errors = DEFAULT_VALUE
        self.started_time = DEFAULT_VALUE
        self.ended_time = DEFAULT_VALUE
        self.files_searched = DEFAULT_VALUE
        self.files_backed_up = DEFAULT_VALUE
        self.bytes_searched = DEFAULT_VALUE
        self.bytes_backed_up = DEFAULT_VALUE
        self.bytes_in_db = DEFAULT_VALUE
        self.bandwidth_avg_bps = DEFAULT_VALUE
        self.snapshot_id = DEFAULT_VALUE


    def to_model(self):
        return models.BackupChange(**self._dict())

    def _dict(self):

        result = dict(
            (key, value)
            for key, value in self.__dict__.items()
            if value != DEFAULT_VALUE
        )

        if "errors" in result:
            result["errors"] = models.Errors(**result["errors"])

        return result
"""
