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

from poppy.manager import base

JSON_HOME = {
    "resources": {
        "rel/poppy": {
            "href-template": "services{?marker,limit}",
            "href-vars": {
                "marker": "param/marker",
                "limit": "param/limit"
            },
            "hints": {
                "allow": [
                    "GET"
                ],
                "formats": {
                    "application/json": {}
                }
            }
        }
    }
}


class DefaultHomeController(base.HomeController):
    """Default Home Controller."""

    def __init__(self, manager):
        super(DefaultHomeController, self).__init__(manager)

        self.JSON_HOME = JSON_HOME

    def get(self):
        """get.

        :return json home
        """
        return self.JSON_HOME
