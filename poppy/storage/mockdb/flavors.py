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

from poppy.model import flavor
from poppy.storage import base


class FlavorsController(base.FlavorsController):

    @property
    def session(self):
        return self._driver.database

    def list(self):
        f = flavor.Flavor(
            "standard",
            [flavor.Provider("mock", "www.mock_provider.com")]
        )
        return [f]

    def get(self, flavor_id):
        f = flavor.Flavor(
            "standard",
            [flavor.Provider("mock", "www.mock_provider.com")]
        )
        if flavor_id == "non_exist":
            raise LookupError("More than one flavor/no record was retrieved.")
        return f

    def add(self, flavor):
        pass

    def delete(self, flavor_id):
        pass
