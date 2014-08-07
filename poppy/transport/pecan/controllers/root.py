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

import re

import pecan

from poppy.transport.pecan.controllers import base


class RootController(base.Controller):

    def __init__(self, driver):
        super(RootController, self).__init__(driver)
        self.paths = []

    def add_controller(self, path, controller):
        super(RootController, self).add_controller(path, controller)
        self.paths.append(path)

    @pecan.expose()
    def _route(self, args, request=None):
        # Optionally allow OpenStack project ID in the URL
        # Remove it from the URL if it's present
        # ['v1.0', 'services'] or ['v1', '123', 'services']
        if (
            len(args) >= 2
            and args[0] in self.paths
            and re.match('^[0-9]+$', args[1])
        ):
            args.pop(1)

        return super(RootController, self)._route(args, request)
