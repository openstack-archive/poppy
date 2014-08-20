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

from poppy.model import service
from poppy.transport.pecan.models.request import domain
from poppy.transport.pecan.models.request import origin


class Model(service.Service):

    'response class for Link'

    def __init__(self, input_json, **kwargs):
        if isinstance(input_json, dict):
            self._temp_obj = service.Service.from_dict_init(input_json)
        else:
            # if it is a string
            self.decoder = self.get_decoder()
            self._temp_obj = self.decoder().decode(input_json)
        super(Model, self).__init__(self._temp_obj.name,
                                    self._temp_obj.origins,
                                    self._temp_obj.domains)

    def get_decoder(self):
        class tempDecoder(json.JSONDecoder):

            def decode(self, s):
                dict_obj = super(tempDecoder, self).decode(s)
                origins = dict_obj.get("origins", [])
                domains = dict_obj.get("domains", [])
                origins = [origin.Model(d) for d in origins]
                domains = [domain.Model(d) for d in domains]
                return service.Service("temp_service", origins, domains)

        return tempDecoder

    @property
    def domains(self):
        # overwrite getter because we need to be able to convert a request
        # model into a model
        return self._domains

    @property
    def origins(self):
        # overwrite getter because we need to be able to convert a request
        # model into a model
        return self._origins
