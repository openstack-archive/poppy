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

CQL_GET_ALL = '''
    SELECT flavor_id,
        providers
    FROM flavors
'''

CQL_GET = '''
    SELECT flavor_id,
        providers
    FROM flavors
    WHERE flavor_id = %(flavor_id)s
'''

CQL_DELETE = '''
    DELETE FROM flavors
    WHERE flavor_id = %(flavor_id)s
'''

CQL_CREATE = '''
    INSERT INTO flavors (flavor_id,
        providers)
    VALUES (%(flavor_id)s,
        %(providers)s)
'''


class FlavorsController(base.FlavorsController):

    @property
    def session(self):
        return self._driver.flavor_database

    def list(self):
        """List the supported flavors."""

        # get all
        result = self.session.execute(CQL_GET_ALL)

        flavors = [
            flavor.Flavor(
                f.flavor_id,
                [flavor.Provider(p_id, p_url)
                    for p_id, p_url in f.providers.items()])
            for f in result]

        return flavors

    def get(self, flavor_id):
        """Get the specified Flavor."""

        args = {
            'flavor_id': flavor_id
        }
        result = self.session.execute(CQL_GET, args)

        flavors = [
            flavor.Flavor(
                f.flavor_id,
                [flavor.Provider(p_id, p_url)
                    for p_id, p_url in f.providers.items()])
            for f in result]

        return flavors

    def add(self, flavor):
        """Add a new flavor."""

        providers = dict((p.provider_id, p.provider_url)
                         for p in flavor.providers)

        args = {
            'flavor_id': flavor.flavor_id,
            'providers': providers
        }

        self.session.execute(CQL_CREATE, args)

    def delete(self, flavor_id, provider_id=None):
        """Delete a flavor."""

        args = {
            'flavor_id': flavor_id
        }
        self.session.execute(CQL_DELETE, args)
