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

try:
    import ordereddict as collections
except ImportError:
    import collections

from pecan import jsonify

from poppy.model import common
from poppy.transport.pecan.models.response import link


class Model(common.DictSerializableModel):

    'Service Response Model.'

    def __init__(self, data_dict):
        self.from_dict(data_dict)

    def encode(self):
        result = collections.OrderedDict({
            "name": self.name,
            "domains": self.domains,
            "origins": self.origins,
            "caching": self.caching,
            "restrictions": self.restrictions,
            "status": self.status
        })
        # TODO(tonytan4ever) : add access_url links.
        # This has things to do with provider_detail change. (CDN-172)
        result["links"] = [link.Model(
                           '/v1.0/services/{0}'.format(self.name),
                           'self')]
        return result


@jsonify.jsonify.register(Model)
def jsonify_model(obj):
    return obj.encode()
