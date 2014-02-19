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

# stevedore/example/simple.py
from cdn.provider import base


class HostController(base.HostBase):

    def list(self):
        print "get list of hostnames from sample"

    def create(self, hostname):
        print "create hostname at sample"

    def delete(self):
        print "delete hostname at sample"

    def get(self):
        print "get hostname from sample"
