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
from poppy.transport.pecan.models.response import cachingrules
from poppy.transport.pecan.models.response import domain
from poppy.transport.pecan.models.response import link
from poppy.transport.pecan.models.response import origin
from poppy.transport.pecan.models.response import restriction


class Model(collections.OrderedDict):

    'Service Response Model.'

    def __init__(self, service_obj, controller):
        super(Model, self).__init__()
        self["name"] = service_obj.name
        self["id"] = str(service_obj.service_id)
        self["domains"] = [domain.Model(d) for d in service_obj.domains]
        self["origins"] = [origin.Model(o) for o in service_obj.origins]
        self["restrictions"] = [restriction.Model(r) for r in
                                service_obj.restrictions]
        self["caching"] = [cachingrules.Model(c) for c in
                           service_obj.caching]
        self["status"] = service_obj.status
        self["flavor_id"] = service_obj.flavor_id

        self["errors"] = []

        self["links"] = [
            link.Model(
                str(
                    uri.encode(u'{0}/services/{1}'.format(
                        controller.base_url,
                        service_obj.service_id))),
                'self'),
            link.Model(
                str(
                    uri.encode(u'{0}/flavors/{1}'.format(
                        controller.base_url,
                        service_obj.flavor_id))),
                'flavor')]

        for provider_name in service_obj.provider_details:
            provider_detail = service_obj.provider_details[provider_name]

            # add the access urls
            access_urls = provider_detail.access_urls
            for access_url in access_urls:
                self["links"].append(link.Model(
                    access_url['operator_url'],
                    'access_url'))

            # add any errors
            error_message = provider_detail.error_message
            if error_message:
                self["errors"].append({"message": error_message})
