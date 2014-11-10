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

from poppy import bootstrap
from poppy.manager import base


class DefaultFlavorsController(base.FlavorsController):
    """Default Flavors Controller."""

    def __init__(self, manager):
        super(DefaultFlavorsController, self).__init__(manager)

    def list(self):
        """list.

        :return list
        """
        return self.storage.list()

    def get(self, flavor_id):
        """get.

        ":param flavor_id
        :return flavor id
        """
        return self.storage.get(flavor_id)

    def add(self, new_flavor):
        """add.

        :param new_flavor
        :return new flavor
        :raise LookupError
        """
        # is this a valid flavor?
        provider_list = self.driver.conf[bootstrap._DRIVER_GROUP].providers

        for provider in new_flavor.providers:
            if provider.provider_id not in provider_list:
                raise LookupError(
                    "{0} is not a valid Provider.  Please choose from {1}"
                    .format(provider.provider_id, provider_list))

        # made it to here, so create it.
        return self.storage.add(new_flavor)

    def delete(self, flavor_id):
        """delete.

        :param flavor_id
        :return flavor_id
        """
        return self.storage.delete(flavor_id)
