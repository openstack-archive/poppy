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

import json

from cdn.storage import base

CQL_GET_ALL_SERVICES = '''
    SELECT project_id,
        service_name,
        domains,
        origins,
        caching_rules,
        restrictions
    FROM services
    WHERE project_id = %(project_id)s
'''

CQL_GET_SERVICE = '''
    SELECT project_id,
        service_name,
        domains,
        origins,
        caching_rules,
        restrictions
    FROM services
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''

CQL_DELETE_SERVICE = '''
    DELETE FROM services
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''

CQL_CREATE_SERVICE = '''
    INSERT INTO services (project_id,
        service_name,
        domains,
        origins,
        caching_rules,
        restrictions)
    VALUES (%(project_id)s,
        %(service_name)s,
        %(domains)s,
        %(origins)s,
        %(caching_rules)s,
        %(restrictions)s)
'''

CQL_UPDATE_DOMAINS = '''
    UPDATE services
    SET domains = %(domains)s
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''

CQL_UPDATE_ORIGINS = '''
    UPDATE services
    SET origins = %(origins)s
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''

CQL_UPDATE_CACHING_RULES = '''
    UPDATE services
    SET caching_rules = %(caching_rules)s
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''

CQL_UPDATE_RESTRICTIONS = '''
    UPDATE services
    SET restrictions = %(restrictions)s
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''


class ServicesController(base.ServicesController):

    @property
    def session(self):
        return self.driver.service_database

    def list(self, project_id):

        # get all services
        args = {
            'project_id': project_id
        }

        result = self.session.execute(CQL_GET_ALL_SERVICES, args)

        # TODO(amitgandhinz) : build the formatted json structure from the
        # result
        # TODO(amitgandhinz): return services instead once its formatted.
        return result

    def get(self, project_id, service_name):
        # get the requested service from storage
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        result = self.session.execute(CQL_GET_SERVICE, args)

        # TODO(amitgandhinz): need to format this return result in the correct
        # format.
        return result

    def create(self, project_id, service_name, service_json):

        # create the service in storage
        service = service_json

        domains = [json.dumps(domain) for domain in service["domains"]]
        origins = [json.dumps(origin) for origin in service["origins"]]
        caching_rules = [json.dumps(caching_rule)
                         for caching_rule in service["caching"]]
        restrictions = [json.dumps(restriction)
                        for restriction in service["restrictions"]]

        # creates a new service
        args = {
            'project_id': project_id,
            'service_name': service_name,
            'domains': domains,
            'origins': origins,
            'caching_rules': caching_rules,
            'restrictions': restrictions
        }

        self.session.execute(CQL_CREATE_SERVICE, args)

    def update(self, project_id, service_name, service_json):
        # update configuration in storage

        # determine what changed.

        # update those columns provided only.
        pass

    def delete(self, project_id, service_name):
        # delete local configuration from storage
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        self.session.execute(CQL_DELETE_SERVICE, args)
