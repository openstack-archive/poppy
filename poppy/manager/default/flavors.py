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


class DefaultFlavorsController(base.FlavorsController):
    def __init__(self, manager):
        super(DefaultFlavorsController, self).__init__(manager)

    def list(self):
        return self.storage.list()

    def get(self, flavor_id):
        return self.storage.get(flavor_id)

    def add(self, new_flavor):
        # do we have a valid extension for the providers
        # listed in this new flavor?

        # TODO(amitgandhinz): Check that the flavor extension exists.

        # Create the flavor
        return self.storage.add(new_flavor)

    def delete(self, flavor_id):
        return self.storage.delete(flavor_id)
