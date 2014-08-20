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

from pecan import jsonify

from poppy.model import common


class Model(common.DictSerializableModel):
    'request class for origin'
    def __init__(self, input_json, **kwargs):
        self.from_dict(input_json)

    def encode(self):
        return self.to_dict()


@jsonify.jsonify.register(Model)
def jsonify_model(obj):
    return obj.encode() 