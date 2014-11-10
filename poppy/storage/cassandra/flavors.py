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
    """Flavors Controller."""

    @property
    def session(self):
        """Get session.

        :returns database
        """
        return self._driver.database

    def list(self):
        """list.

        :returns list List the supported flavors
        """

        # get all
        result = self.session.execute(CQL_GET_ALL)

        flavors = [
            flavor.Flavor(
                f['flavor_id'],
                [flavor.Provider(p_id, p_url)
                 for p_id, p_url in f['providers'].items()]
                if f['providers'] is not None else [])
            for f in result]

        return flavors

    def get(self, flavor_id):
        """get.

        :param flavor_id
        :returns flavor The specified Flavor
        """
        args = {
            'flavor_id': flavor_id
        }
        result = self.session.execute(CQL_GET, args)

        flavors = [
            flavor.Flavor(
                f['flavor_id'],
                [flavor.Provider(p_id, p_url)
                 for p_id, p_url in f['providers'].items()]
                if f['providers'] is not None else []
            )
            for f in result]

        if (len(flavors) == 1):
            return flavors[0]
        elif (len(flavors) > 1):
            raise LookupError(
                u"More than one flavor with the id '{0}' was retrieved."
                .format(flavor_id))
        else:
            raise LookupError(
                u"Could not find a flavor with the id '{0}'".format(flavor_id))

    def add(self, flavor):
        """add.

        Add a new flavor

        :param flavor
        :raises ValueError
        """

        # check if the flavor already exist.
        # Note: If it does, no LookupError will be raised
        try:
            self.get(flavor.flavor_id)
        except LookupError:
            pass
        else:
            raise ValueError("A flavor with the id '%s' already exists"
                             % flavor.flavor_id)

        providers = dict((p.provider_id, p.provider_url)
                         for p in flavor.providers)

        args = {
            'flavor_id': flavor.flavor_id,
            'providers': providers
        }

        self.session.execute(CQL_CREATE, args)

    def delete(self, flavor_id):
        """delete.

        Delete a flavor.

        :param flavor_id
        """

        args = {
            'flavor_id': flavor_id
        }
        self.session.execute(CQL_DELETE, args)
