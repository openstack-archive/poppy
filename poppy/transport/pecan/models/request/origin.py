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

from poppy.model.helpers import origin
from poppy.transport.pecan.models.request import rule


def load_from_json(json_data):
    origin_name = json_data.get("origin")
    origin_name = origin_name.rstrip("/")
    hostheadertype = json_data.get("hostheadertype", "domain")
    hostheadervalue = json_data.get("hostheadervalue", None)
    port = json_data.get("port", 80)
    ssl = json_data.get("ssl", False)
    rules = json_data.get("rules", [])
    rules = [rule.load_from_json(r) for r in rules]
    result = origin.Origin(origin=origin_name, hostheadertype=hostheadertype,
                           hostheadervalue=hostheadervalue, port=port,
                           ssl=ssl)
    result.rules = rules
    return result
