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

server = {
    'port': '8080',
    'host': '0.0.0.0'
}

app = {
    'root': 'tests.functional.transport.pecan.mock_ep.MockPecanEndpoint',
    'modules': ['tests.functional.transport.pecan.pecan_app'],
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}
