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

from poppy.model.helpers import rule


def load_from_json(json_data):
    name = json_data.get('name', None)
    res = rule.Rule(name)
    res.referrer = json_data.get('referrer', None)
    res.http_host = json_data.get('http_host', None)
    res.http_method = json_data.get('http_method', None)
    res.client_ip = json_data.get('client_ip', None)
    res.request_url = json_data.get('request_url', None)
    res.geography = json_data.get('geography', None)
    return res
