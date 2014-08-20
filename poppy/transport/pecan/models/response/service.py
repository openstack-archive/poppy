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

from poppy.transport.pecan.models.response import domain
from poppy.transport.pecan.models.response import link
from poppy.transport.pecan.models.response import origin


class Model(collections.OrderedDict):

    'Service Response Model.'

    def __init__(self, service_obj):
        super(Model, self).__init__()
        self["name"] = service_obj.name,
        self["domains"] = [domain.Model(d) for d in service_obj.domains]
        self["origins"] = [origin.Model(o) for o in service_obj.origins]
        self["status"] = service_obj.status

        # TODO(tonytan4ever) : add access_url links.
        # This has things to do with provider_detail change. (CDN-172)
        self["links"] = [link.Model(
            '/v1.0/services/{0}'.format(self["name"]),
            'self')]
