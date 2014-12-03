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
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

from poppy.common import uri
from poppy.transport.pecan.models.response import domain
from poppy.transport.pecan.models.response import link
from poppy.transport.pecan.models.response import origin
from poppy.transport.pecan.models.response import restriction


class Model(collections.OrderedDict):

    'Service Response Model.'

    def __init__(self, service_obj, request):
        super(Model, self).__init__()
        self["name"] = service_obj.name
        self["domains"] = [domain.Model(d) for d in service_obj.domains]
        self["origins"] = [origin.Model(o) for o in service_obj.origins]
        self["restrictions"] = [restriction.Model(r) for r in
                                service_obj.restrictions]
        self["status"] = service_obj.status
        self["flavor_id"] = service_obj.flavor_id

        # TODO(tonytan4ever) : add access_url links.
        # This has things to do with provider_detail change. (CDN-172)
        self["links"] = [
            link.Model(
                str(
                    uri.encode(u'{0}/v1.0/services/{1}'.format(
                        request.host_url,
                        self['name']))),
                'self'),
            link.Model(
                str(
                    uri.encode(u'{0}/v1.0/flavors/{1}'.format(
                        request.host_url,
                        service_obj.flavor_id))),
                'flavor')]

        for provider_name in service_obj.provider_details:
            for access_url in (
                    service_obj.provider_details[provider_name].access_urls):
                self["links"].append(link.Model(
                    access_url,
                    'access_url'))
