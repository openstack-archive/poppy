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

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model import service
from poppy.storage import base


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

CQL_GET_PROVIDER_DETAILS = '''
    SELECT provider_details
    FROM services
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''


class ServicesController(base.ServicesController):

    @property
    def session(self):
        return self._driver.database

    def list(self, project_id, marker=None, limit=None):

        # get all services
        args = {
            'project_id': project_id
        }

        results = self.session.execute(CQL_GET_ALL_SERVICES, args)

        # TODO(amitgandhinz) : build the formatted json structure from the
        # result
        # TODO(amitgandhinz): return services instead once its formatted.
        services = []
        for r in results:
            name = r.get("name", "unnamed")
            origins = r.get("origins", [])
            domains = r.get("domains", [])
            origins = [origin.Origin(json.loads(o)['origin'],
                                     json.loads(o).get("port", 80),
                                     json.loads(o).get("ssl", False))
                       for o in origins]
            domains = [domain.Domain(json.loads(d)['domain']) for d in domains]
            services.append(service.Service(name, domains, origins))
        return services

    def get(self, project_id, service_name):
        # get the requested service from storage
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        results = self.session.execute(CQL_GET_SERVICE, args)

        if len(results) != 1:
            raise ValueError("No service or multiple service found: %s"
                             % service_name)

        services = []
        for r in results:
            name = r.get("name", "unnamed")
            origins = r.get("origins", [])
            domains = r.get("domains", [])
            origins = [origin.Origin(json.loads(o)['origin'],
                                     json.loads(o).get("port", 80),
                                     json.loads(o).get("ssl", False))
                       for o in origins]
            domains = [domain.Domain(json.loads(d)['domain']) for d in domains]
            services.append(service.Service(name, domains, origins))
        return services[0]

    def create(self, project_id, service_name, service_obj):

        # create the service in storage
        domains = [json.dumps(domain.to_dict())
                   for domain in service_obj.domains]
        origins = [json.dumps(origin.to_dict())
                   for origin in service_obj.origins]
        caching_rules = [json.dumps(caching_rule.to_dict())
                         for caching_rule in service_obj.caching]
        restrictions = [json.dumps(restriction)
                        for restriction in service_obj.restrictions]

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

    def update(self, project_id, service_name, service_obj):
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

    def get_provider_details(self, project_id, service_name):
        # TODO(tonytan4ever): Use real CQL read provider details info
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        # TODO(tonytan4ever): Not sure this returns a list or a single
        # dictionary.
        # Needs to verify after cassandra unittest framework has been added in
        # if a list, the return the first item of a list. if it is a dictionary
        # returns the dictionary
        exec_results = self.session.execute(CQL_GET_PROVIDER_DETAILS, args)
        results = {}
        for provider_name in exec_results[0]:
            provider_detail_dict = json.loads(exec_results[0][provider_name])
            id = provider_detail_dict.get("id", None)
            access_url = provider_detail_dict.get("access_url", None)
            status = provider_detail_dict.get("status", u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                id=id,
                access_url=access_url,
                status=status)
            results[provider_name] = provider_detail_obj
        return results
