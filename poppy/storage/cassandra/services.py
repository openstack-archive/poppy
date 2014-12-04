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

from poppy.model.helpers import cachingrule
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model.helpers import restriction
from poppy.model.helpers import rule
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

CQL_LIST_SERVICES = '''
    SELECT project_id,
        service_name,
        domains,
        flavor_id,
        origins,
        caching_rules,
        restrictions,
        provider_details
    FROM services
    WHERE project_id = %(project_id)s
        AND service_name > %(service_name)s
    ORDER BY service_name
    LIMIT %(limit)s
'''

CQL_GET_SERVICE = '''
    SELECT project_id,
        service_name,
        flavor_id,
        domains,
        flavor_id,
        origins,
        caching_rules,
        restrictions,
        provider_details
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
        flavor_id,
        domains,
        origins,
        caching_rules,
        restrictions,
        provider_details
        )
    VALUES (%(project_id)s,
        %(service_name)s,
        %(flavor_id)s,
        %(domains)s,
        %(origins)s,
        %(caching_rules)s,
        %(restrictions)s,
        %(provider_details)s)
'''

CQL_UPDATE_SERVICE = CQL_CREATE_SERVICE

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

CQL_UPDATE_PROVIDER_DETAILS = '''
    UPDATE services
    set provider_details = %(provider_details)s
    WHERE project_id = %(project_id)s AND service_name = %(service_name)s
'''


class ServicesController(base.ServicesController):

    """Services Controller."""

    @property
    def session(self):
        """Get session.

        :returns session
        """
        return self._driver.database

    def list(self, project_id, marker, limit):
        """list.

        :param project_id
        :param marker
        :param limit

        :returns services
        """
        # list services
        args = {
            'project_id': project_id,
            'service_name': marker,
            'limit': limit
        }

        results = self.session.execute(CQL_LIST_SERVICES, args)
        services = [self.format_result(r) for r in results]

        return services

    def get(self, project_id, service_name):
        """get.

        :param project_id
        :param service_name

        :returns result The requested service
        :raises ValueError
        """
        # get the requested service from storage
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        results = self.session.execute(CQL_GET_SERVICE, args)

        if len(results) != 1:
            raise ValueError('No service or multiple service found: %s'
                             % service_name)

        # at this point, it is certain that there's exactly 1 result in
        # results.
        result = results[0]

        return self.format_result(result)

    def create(self, project_id, service_obj):
        """create.

        :param project_id
        :param service_obj

        :raises ValueError
        """
        # create the service in storage
        service_name = service_obj.name

        # check if the serivce already exist.
        # Note: If it does, no LookupError will be raised
        try:
            self.get(project_id, service_name)
        except ValueError:  # this value error means this service doesn't exist
            pass
        else:
            raise ValueError("Service %s already exists..." % service_name)

        domains = [json.dumps(d.to_dict())
                   for d in service_obj.domains]
        origins = [json.dumps(o.to_dict())
                   for o in service_obj.origins]
        caching_rules = [json.dumps(caching_rule.to_dict())
                         for caching_rule in service_obj.caching]
        restrictions = [json.dumps(r.to_dict())
                        for r in service_obj.restrictions]

        # creates a new service
        args = {
            'project_id': project_id,
            'service_name': service_name,
            'flavor_id': service_obj.flavor_ref,
            'domains': domains,
            'origins': origins,
            'caching_rules': caching_rules,
            'restrictions': restrictions,
            'provider_details': {}
        }

        self.session.execute(CQL_CREATE_SERVICE, args)

    def update(self, project_id, service_name, service_obj):

        domains = [json.dumps(d.to_dict())
                   for d in service_obj.domains]
        origins = [json.dumps(o.to_dict())
                   for o in service_obj.origins]
        caching_rules = [json.dumps(caching_rule.to_dict())
                         for caching_rule in service_obj.caching]
        restrictions = [json.dumps(r.to_dict())
                        for r in service_obj.restrictions]

        # updates an existing new service
        args = {
            'project_id': project_id,
            'service_name': service_name,
            'flavor_id': service_obj.flavor_ref,
            'domains': domains,
            'origins': origins,
            'caching_rules': caching_rules,
            'restrictions': restrictions,
            'provider_details': {}
        }

        self.session.execute(CQL_UPDATE_SERVICE, args)

    def delete(self, project_id, service_name):
        """delete.

        Delete local configuration storage
        """
        # delete local configuration from storage
        args = {
            'project_id': project_id,
            'service_name': service_name
        }
        self.session.execute(CQL_DELETE_SERVICE, args)

    def get_provider_details(self, project_id, service_name):
        """get_provider_details.

        :param project_id
        :param service_name
        :returns results Provider details
        """

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

        provider_details_result = exec_results[0]['provider_details'] or {}
        results = {}
        for provider_name in provider_details_result:
            provider_detail_dict = json.loads(
                provider_details_result[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get("access_urls", [])
            status = provider_detail_dict.get("status", u'creating')
            error_info = provider_detail_dict.get("error_info", None)
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status,
                error_info=error_info)
            results[provider_name] = provider_detail_obj
        return results

    def update_provider_details(self, project_id, service_name,
                                provider_details):
        """update_provider_details.

        :param project_id
        :param service_name
        :param provider_details
        """
        provider_detail_dict = {}
        for provider_name in provider_details:
            provider_detail_dict[provider_name] = json.dumps({
                "id": provider_details[provider_name].provider_service_id,
                "access_urls": provider_details[provider_name].access_urls,
                "status": provider_details[provider_name].status,
                "name": provider_details[provider_name].name,
                "error_info": provider_details[provider_name].error_info
            })
        args = {
            'project_id': project_id,
            'service_name': service_name,
            'provider_details': provider_detail_dict
        }
        # TODO(tonytan4ever): Not sure this returns a list or a single
        # dictionary.
        # Needs to verify after cassandra unittest framework has been added in
        # if a list, the return the first item of a list. if it is a dictionary
        # returns the dictionary
        self.session.execute(CQL_UPDATE_PROVIDER_DETAILS, args)

    @staticmethod
    def format_result(result):
        """format_result.

        :param result
        :returns formatted result
        """
        name = result.get('service_name')

        flavor_ref = result.get('flavor_id')
        origins = [json.loads(o) for o in result.get('origins', []) or []]
        domains = [json.loads(d) for d in result.get('domains', []) or []]
        restrictions = [json.loads(r)
                        for r in result.get('restrictions', []) or []]
        caching_rules = [json.loads(c) for c in result.get('caching_rules', [])
                         or []]

        # create models for each item
        origins = [
            origin.Origin(
                o['origin'],
                o.get('port', 80),
                o.get('ssl', False), [
                    rule.Rule(
                        rule_i.get('name'),
                        request_url=rule_i.get('request_url'))
                    for rule_i in o.get(
                        'rules', [])]) for o in origins]

        domains = [domain.Domain(d['domain'])
                   for d in domains]

        restrictions = [restriction.Restriction(
            r.get('name'),
            [rule.Rule(r_rule.get('name'),
                       referrer=r_rule.get('referrer'))
             for r_rule in r['rules']])
            for r in restrictions]

        caching_rules = [cachingrule.CachingRule(
            caching_rule.get('name'),
            caching_rule.get('ttl'),
            [rule.Rule(rule_i.get('name'),
                       referrer=rule_i.get('request_url'))
             for rule_i in caching_rule['rules']])
            for caching_rule in caching_rules]

        # create the service object
        s = service.Service(name, domains, origins, flavor_ref,
                            caching=caching_rules,
                            restrictions=restrictions)

        # format the provider details
        provider_detail_results = result.get('provider_details') or {}
        provider_details_dict = {}
        for provider_name in provider_detail_results:
            provider_detail_dict = json.loads(
                provider_detail_results[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'unknown')
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status)
            provider_details_dict[provider_name] = provider_detail_obj
        s.provider_details = provider_details_dict

        # return the service
        return s
