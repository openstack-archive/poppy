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

import datetime
import json
import uuid
try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

from cassandra import query
from oslo_log import log

from poppy.model.helpers import cachingrule
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model.helpers import restriction
from poppy.model.helpers import rule
from poppy.model import log_delivery as ld
from poppy.model import service
from poppy.storage import base

LOG = log.getLogger(__name__)


CQL_LIST_SERVICES = '''
    SELECT project_id,
        service_id,
        service_name,
        domains,
        flavor_id,
        origins,
        caching_rules,
        restrictions,
        provider_details,
        operator_status,
        log_delivery
    FROM services
    WHERE project_id = %(project_id)s
        AND service_id > %(marker)s
    ORDER BY service_id
    LIMIT %(limit)s
'''

CQL_GET_SERVICE = '''
    SELECT project_id,
        service_id,
        service_name,
        flavor_id,
        domains,
        origins,
        caching_rules,
        restrictions,
        provider_details,
        operator_status,
        log_delivery
    FROM services
    WHERE project_id = %(project_id)s AND service_id = %(service_id)s
'''

CQL_VERIFY_DOMAIN = '''
    SELECT project_id,
        service_id,
        domain_name
    FROM domain_names
    WHERE domain_name = %(domain_name)s
'''

CQL_SEARCH_BY_DOMAIN = CQL_VERIFY_DOMAIN

CQL_GET_SERVICE_COUNT = '''
    SELECT COUNT(*) FROM services
    WHERE project_id = %(project_id)s
'''

CQL_SET_SERVICE_LIMIT = '''
    UPDATE service_limits set project_limit = %(project_limit)s
    WHERE project_id = %(project_id)s
'''

CQL_GET_SERVICE_LIMIT = '''
    SELECT project_limit FROM service_limits
    WHERE project_id = %(project_id)s
'''

CQL_CLAIM_DOMAIN = '''
    INSERT INTO domain_names (domain_name,
        project_id,
        service_id)
    VALUES (%(domain_name)s,
        %(project_id)s,
        %(service_id)s)
'''

CQL_RELINQUISH_DOMAINS = '''
    DELETE FROM domain_names
    WHERE domain_name IN %(domain_list)s
'''

CQL_ARCHIVE_SERVICE = '''
    BEGIN BATCH
        INSERT INTO archives (project_id,
            service_id,
            service_name,
            flavor_id,
            domains,
            origins,
            caching_rules,
            restrictions,
            provider_details,
            operator_status,
            archived_time
            )
        VALUES (%(project_id)s,
            %(service_id)s,
            %(service_name)s,
            %(flavor_id)s,
            %(domains)s,
            %(origins)s,
            %(caching_rules)s,
            %(restrictions)s,
            %(provider_details)s,
            %(operator_status)s,
            %(archived_time)s)

        DELETE FROM services
        WHERE project_id = %(project_id)s AND service_id = %(service_id)s;

        DELETE FROM domain_names
        WHERE domain_name IN %(domains_list)s

    APPLY BATCH;
    '''
CQL_DELETE_SERVICE = '''
    BEGIN BATCH
        DELETE FROM services
        WHERE project_id = %(project_id)s AND service_id = %(service_id)s

        DELETE FROM domain_names
        WHERE domain_name IN %(domains_list)s
    APPLY BATCH
'''

CQL_CREATE_SERVICE = '''
    INSERT INTO services (project_id,
        service_id,
        service_name,
        flavor_id,
        domains,
        origins,
        caching_rules,
        restrictions,
        provider_details,
        operator_status,
        log_delivery
        )
    VALUES (%(project_id)s,
        %(service_id)s,
        %(service_name)s,
        %(flavor_id)s,
        %(domains)s,
        %(origins)s,
        %(caching_rules)s,
        %(restrictions)s,
        %(provider_details)s,
        %(operator_status)s,
        %(log_delivery)s)
'''


CQL_UPDATE_SERVICE = CQL_CREATE_SERVICE

CQL_GET_PROVIDER_DETAILS = '''
    SELECT provider_details
    FROM services
    WHERE project_id = %(project_id)s AND service_id = %(service_id)s
'''

CQL_UPDATE_PROVIDER_DETAILS = '''
    UPDATE services
    set provider_details = %(provider_details)s
    WHERE project_id = %(project_id)s AND service_id = %(service_id)s
'''

CQL_UPDATE_CERT_DETAILS = '''
    UPDATE certificate_info
    set cert_details = %(cert_details)s
    WHERE domain_name = %(domain_name)s
    IF cert_type = %(cert_type)s AND flavor_id = %(flavor_id)s
'''

CQL_SET_SERVICE_STATUS = '''
    INSERT INTO service_status (service_id,
        project_id,
        status
        )
    VALUES (%(service_id)s,
        %(project_id)s,
        %(status)s)
'''

CQL_SET_PROVIDER_URL = '''
    INSERT INTO provider_url_domain(provider_url,
    domain_name)
    VALUES (%(provider_url)s, %(domain_name)s)
'''

CQL_DELETE_PROVIDER_URL = '''
    DELETE FROM provider_url_domain
    WHERE provider_url = %(provider_url)s
    AND domain_name = %(domain_name)s
'''

CQL_GET_BY_PROVIDER_URL = '''
    SELECT domain_name FROM provider_url_domain
    WHERE provider_url = %(provider_url)s
'''

CQL_GET_SERVICE_STATUS = '''
    SELECT project_id,
        service_id
    FROM service_status
    WHERE status = %(status)s
'''

CQL_DELETE_SERVICE_STATUS = '''
    DELETE FROM service_status
    WHERE service_id = %(service_id)s
'''


class ServicesController(base.ServicesController):

    """Services Controller."""

    @property
    def session(self):
        """Get session.

        :returns session
        """
        return self._driver.database

    def get_services(self, project_id, marker, limit):
        """list.

        :param project_id
        :param marker
        :param limit

        :returns services
        """
        # list services
        if marker is None:
            marker = '00000000-00000000-00000000-00000000'

        args = {
            'project_id': project_id,
            'marker': uuid.UUID(str(marker)),
            'limit': limit
        }

        stmt = query.SimpleStatement(
            CQL_LIST_SERVICES,
            consistency_level=self._driver.consistency_level)
        results = self.session.execute(stmt, args)
        services = [self.format_result(r) for r in results]

        return services

    def get_service(self, project_id, service_id):
        """get.

        :param project_id
        :param service_id

        :returns result The requested service
        :raises ValueError
        """
        # get the requested service from storage
        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id))
        }
        stmt = query.SimpleStatement(
            CQL_GET_SERVICE,
            consistency_level=self._driver.consistency_level)
        result_set = self.session.execute(stmt, args)
        complete_result = list(result_set)
        if len(complete_result) != 1:
            raise ValueError('No service found: %s'
                             % service_id)

        # at this point, it is certain that there's exactly 1 result in
        # results.
        result = complete_result[0]

        return self.format_result(result)

    def domain_exists_elsewhere(self, domain_name, service_id):
        """domain_exists_elsewhere

        Check if a service with this domain name has already been created.

        :param domain_name
        :param service_id

        :raises ValueError
        :returns Boolean if the service exists with another user.
        """
        try:
            LOG.info("Check if domain '{0}' exists".format(domain_name))
            args = {
                'domain_name': domain_name.lower()
            }
            stmt = query.SimpleStatement(
                CQL_VERIFY_DOMAIN,
                consistency_level=self._driver.consistency_level)
            results = self.session.execute(stmt, args)

            if results:
                LOG.info("Checking for domain '{0}' "
                         "existence yielded {1}".format(domain_name,
                                                        str(results)))
                for r in results:
                    if str(r.get('service_id')) != str(service_id):
                        LOG.info(
                            "Domain '{0}' has already been taken."
                            .format(domain_name))
                        return True
                return False
            else:
                LOG.info("Checking if domain '{0}' exists, "
                         "yielded no results".format(domain_name))
                return False
        except ValueError as ex:
                LOG.warning("Checking for domain '{0}' "
                            "failed!".format(domain_name))
                LOG.exception(ex)
                return False

    def get_service_count(self, project_id):
        """get_service_count

        Fetch Count of Services per project_id.
        :param project_id
        :returns count

        """

        LOG.info("Fetching number of services "
                 "for project_id: {0}".format(project_id))

        args = {
            'project_id': project_id
        }

        stmt = query.SimpleStatement(
            CQL_GET_SERVICE_COUNT,
            consistency_level=self._driver.consistency_level)
        results = self.session.execute(stmt, args)
        complete_result_set = list(results)
        result = complete_result_set[0]

        count = result.get('count', 0)

        LOG.info("Fetched {0} number of services "
                 "for project_id: {1}".format(count, project_id))
        return count

    def get_services_by_status(self, status):

        LOG.info("Fetching service_ids and "
                 "project_ids with status: {0}".format(status))

        args = {
            'status': status
        }

        stmt = query.SimpleStatement(
            CQL_GET_SERVICE_STATUS,
            consistency_level=self._driver.consistency_level)

        result_set = self.session.execute(stmt, args)
        complete_results = list(result_set)
        for result in complete_results:
            result['service_id'] = str(result['service_id'])

        return complete_results

    def delete_services_by_status(self, project_id, service_id, status):

        LOG.info("Deleting service_id: {0} "
                 "with project_id: {1} with status: {2} from service_status "
                 "column family".format(service_id, project_id, status))

        args = {
            'service_id': uuid.UUID(str(service_id))
        }

        stmt = query.SimpleStatement(
            CQL_DELETE_SERVICE_STATUS,
            consistency_level=self._driver.consistency_level)

        self.session.execute(stmt, args)

    def get_domains_by_provider_url(self, provider_url):

        LOG.info("Getting domains by provider_url: {0}".format(provider_url))

        get_domain_provider_url_args = {
            'provider_url': provider_url,
        }

        stmt = query.SimpleStatement(
            CQL_GET_BY_PROVIDER_URL,
            consistency_level=self._driver.consistency_level)

        result_set = self.session.execute(stmt, get_domain_provider_url_args)

        return list(result_set)

    def delete_provider_url(self, provider_url, domain_name):

        LOG.info("Deleting provider_url: {0} and "
                 "domain_name: {1} from provider_url_domain "
                 "column family".format(provider_url, domain_name))

        del_provider_url_args = {
            'provider_url': provider_url,
            'domain_name': domain_name
        }

        stmt = query.SimpleStatement(
            CQL_DELETE_PROVIDER_URL,
            consistency_level=self._driver.consistency_level)

        self.session.execute(stmt, del_provider_url_args)

    def get_service_limit(self, project_id):
        """get_service_limit

        Fetch Current limit on number of services per project_id.

        :param project_id
        :raises ValueError
        :returns limit, if limit exists else default.
        """
        max_services = self._driver.max_services_conf.max_services_per_project

        try:
            LOG.info("Checking if non-default service "
                     "limit exists for "
                     "project_id: {0} ".format(project_id))

            args = {
                'project_id': project_id,
            }
            stmt = query.SimpleStatement(
                CQL_GET_SERVICE_LIMIT,
                consistency_level=self._driver.consistency_level)
            result_set = self.session.execute(stmt, args)
            complete_results = list(result_set)
            if complete_results:
                LOG.info("Checking for service limit for project_id: '{0}' "
                         "existence yielded {1}".format(project_id,
                                                        str(complete_results)))

                result = complete_results[0]

                project_limit = \
                    result.get('project_limit',
                               max_services)
                return project_limit
            else:
                LOG.info("Checking for service limit for project_id: '{0}' "
                         ""
                         "did not yield results, "
                         "therefore defaulting "
                         "to {1}".format(project_id,
                                         max_services))
                return max_services

        except ValueError as ex:
                LOG.warning("Checking if non-default service"
                            "limit exists for"
                            "project_id: {0} failed!".format(project_id))
                LOG.exception(ex)
                return max_services

    def set_service_limit(self, project_id, project_limit):
        """set_service_limit

        Set Current limit on number of services per project_id.

        :param project_id
        :param project_limit

        """

        LOG.info("Setting service"
                 "limit for"
                 "project_id: {0} to be {1}".format(project_id,
                                                    project_limit))
        args = {
            'project_limit': project_limit,
            'project_id': project_id,
        }
        stmt = query.SimpleStatement(
            CQL_SET_SERVICE_LIMIT,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, args)

        LOG.info("service limit for "
                 "project_id: {0} set to be {1}".format(project_id,
                                                        project_limit))

    def set_service_provider_details(self, project_id, service_id, status):
        """set_service_provider_details

        Set current status on service_id under project_id.

        :param project_id
        :param service_id
        :param status
        """

        LOG.info("Setting service "
                 "status for "
                 "service_id : {0}, "
                 "project_id: {1} to be {2}".format(service_id,
                                                    project_id,
                                                    status))
        status_args = {
            'service_id': uuid.UUID(str(service_id)),
            'project_id': project_id,
            'status': status
        }

        stmt = query.SimpleStatement(
            CQL_SET_SERVICE_STATUS,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, status_args)

        provider_details_dict = self.get_provider_details(
            project_id=project_id,
            service_id=service_id)

        for provider_name in sorted(provider_details_dict.keys()):
            provider_details_dict[provider_name].status = status

        self.update_provider_details(
            project_id=project_id,
            service_id=service_id,
            new_provider_details=provider_details_dict
        )

    def create_service(self, project_id, service_obj):
        """create.

        :param project_id
        :param service_obj

        :raises ValueError
        """

        # check if the service domain names already exist
        for d in service_obj.domains:
            if self.domain_exists_elsewhere(
                    d.domain,
                    service_obj.service_id) is True:
                raise ValueError(
                    "Domain %s has already been taken" % d.domain)

        # create the service in storage
        service_id = service_obj.service_id
        service_name = service_obj.name
        domains = [json.dumps(d.to_dict())
                   for d in service_obj.domains]
        origins = [json.dumps(o.to_dict())
                   for o in service_obj.origins]
        caching_rules = [json.dumps(caching_rule.to_dict())
                         for caching_rule in service_obj.caching]
        restrictions = [json.dumps(r.to_dict())
                        for r in service_obj.restrictions]
        log_delivery = json.dumps(service_obj.log_delivery.to_dict())

        # create a new service
        service_args = {
            'project_id': project_id,
            'service_id': uuid.UUID(service_id),
            'service_name': service_name,
            'flavor_id': service_obj.flavor_id,
            'domains': domains,
            'origins': origins,
            'caching_rules': caching_rules,
            'restrictions': restrictions,
            'log_delivery': log_delivery,
            'provider_details': {},
            'operator_status': 'enabled'
        }

        LOG.debug("Creating New Service - {0} ({1})".format(service_id,
                                                            service_name))
        batch = query.BatchStatement(
            consistency_level=self._driver.consistency_level)
        batch.add(query.SimpleStatement(CQL_CREATE_SERVICE), service_args)

        for d in service_obj.domains:
            domain_args = {
                'domain_name': d.domain,
                'project_id': project_id,
                'service_id': uuid.UUID(service_id),
            }
            batch.add(query.SimpleStatement(CQL_CLAIM_DOMAIN), domain_args)

        self.session.execute(batch)

    def update_service(self, project_id, service_id, service_obj):
        """update.

        :param project_id
        :param service_id
        :param service_obj
        """

        service_name = service_obj.name
        domains = [json.dumps(d.to_dict())
                   for d in service_obj.domains]
        origins = [json.dumps(o.to_dict())
                   for o in service_obj.origins]
        caching_rules = [json.dumps(caching_rule.to_dict())
                         for caching_rule in service_obj.caching]
        restrictions = [json.dumps(r.to_dict())
                        for r in service_obj.restrictions]

        pds = {provider:
               json.dumps(service_obj.provider_details[provider].to_dict())
               for provider in service_obj.provider_details}
        status = None
        for provider in service_obj.provider_details:
            status = service_obj.provider_details[provider].status
        log_delivery = json.dumps(service_obj.log_delivery.to_dict())
        # fetch current domains
        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id)),
        }
        stmt = query.SimpleStatement(
            CQL_GET_SERVICE,
            consistency_level=self._driver.consistency_level)

        result_set = self.session.execute(stmt, args)
        complete_results = list(result_set)
        result = complete_results[0]

        # updates an existing service
        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id)),
            'service_name': service_name,
            'flavor_id': service_obj.flavor_id,
            'domains': domains,
            'origins': origins,
            'caching_rules': caching_rules,
            'restrictions': restrictions,
            'provider_details': pds,
            'log_delivery': log_delivery,
            'operator_status': service_obj.operator_status
        }

        stmt = query.SimpleStatement(
            CQL_UPDATE_SERVICE,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, args)

        self.set_service_provider_details(project_id, service_id, status)
        # claim new domains
        batch_claim = query.BatchStatement(
            consistency_level=self._driver.consistency_level)
        for d in service_obj.domains:
            domain_args = {
                'domain_name': d.domain,
                'project_id': project_id,
                'service_id': uuid.UUID(str(service_id))
            }
            batch_claim.add(query.SimpleStatement(CQL_CLAIM_DOMAIN),
                            domain_args)
        self.session.execute(batch_claim)

        # NOTE(TheSriram): We claim (CQL_CLAIM_DOMAIN) all the domains,
        # that got passed in. Now we create a set out of domains_new
        # (current domains present) and domains_old (domains present before
        # we made the current call). The set difference between old and new,
        # are the domains we need to delete (CQL_RELINQUISH_DOMAINS).

        domains_old = set([json.loads(d).get('domain')
                           for d in result.get('domains', []) or []])
        domains_new = set([json.loads(d).get('domain') for d in domains or []])

        # delete domains that no longer exist
        # relinquish old domains

        domains_delete = domains_old.difference(domains_new)
        if domains_delete:
            args = {
                'domain_list': query.ValueSequence(domains_delete)
            }
            stmt = query.SimpleStatement(
                CQL_RELINQUISH_DOMAINS,
                consistency_level=self._driver.consistency_level)
            self.session.execute(stmt, args)

    def update_state(self, project_id, service_id, state):
        """Update service state

        :param project_id
        :param service_id
        :param state

        :returns service_obj
        """

        service_obj = self.get_service(project_id, service_id)
        service_obj.operator_status = state
        self.update_service(project_id, service_id, service_obj)

        return service_obj

    def delete_service(self, project_id, service_id):
        """delete.

        Archive local configuration storage
        """
        # delete local configuration from storage
        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id)),
        }

        # get the existing service
        stmt = query.SimpleStatement(
            CQL_GET_SERVICE,
            consistency_level=self._driver.consistency_level)
        resultset = self.session.execute(stmt, args)
        complete_result = list(resultset)

        result = complete_result[0]

        if result:
            domains_list = [json.loads(d).get('domain')
                            for d in result.get('domains', []) or []]
            # NOTE(obulpathi): Convert a OrderedMapSerializedKey to a Dict
            pds = result.get('provider_details', {}) or {}
            pds = {key: value for key, value in pds.items()}
            status = None
            provider_urls_domain = []

            for provider in pds:
                pds_provider_dict = json.loads(pds.get(provider, {}))
                status = pds_provider_dict.get('status', '')
                access_urls = pds_provider_dict.get('access_urls', [])
                for access_url in access_urls:
                    provider_url = access_url.get('provider_url', None)
                    domain = access_url.get('domain', None)
                    if provider_url and domain:
                        provider_urls_domain.append((provider_url, domain))

            self.delete_services_by_status(project_id, service_id, status)

            for provider_url_domain in provider_urls_domain:
                provider_url, domain = provider_url_domain
                self.delete_provider_url(provider_url, domain)

            if self._driver.archive_on_delete:
                archive_args = {
                    'project_id': result.get('project_id'),
                    'service_id': result.get('service_id'),
                    'service_name': result.get('service_name'),
                    'flavor_id': result.get('flavor_id'),
                    'domains': result.get('domains', []),
                    'origins': result.get('origins', []),
                    'caching_rules': result.get('caching_rules', []),
                    'restrictions': result.get('restrictions', []),
                    'provider_details': pds,
                    'operator_status': result.get('operator_status',
                                                  'enabled'),
                    'archived_time': datetime.datetime.utcnow(),
                    'domains_list': query.ValueSequence(domains_list)
                }

                # archive and delete the service
                stmt = query.SimpleStatement(
                    CQL_ARCHIVE_SERVICE,
                    consistency_level=self._driver.consistency_level)
                self.session.execute(stmt, archive_args)
            else:
                delete_args = {
                    'project_id': result.get('project_id'),
                    'service_id': result.get('service_id'),
                    'domains_list': query.ValueSequence(domains_list)
                }
                stmt = query.SimpleStatement(
                    CQL_DELETE_SERVICE,
                    consistency_level=self._driver.consistency_level)
                self.session.execute(stmt, delete_args)

    def get_provider_details(self, project_id, service_id):
        """get_provider_details.

        :param project_id
        :param service_id
        :returns results Provider details
        """

        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id))
        }
        # TODO(tonytan4ever): Not sure this returns a list or a single
        # dictionary.
        # Needs to verify after cassandra unittest framework has been added in
        # if a list, the return the first item of a list. if it is a dictionary
        # returns the dictionary
        stmt = query.SimpleStatement(
            CQL_GET_PROVIDER_DETAILS,
            consistency_level=self._driver.consistency_level)
        exec_results_set = self.session.execute(stmt, args)
        complete_results = list(exec_results_set)
        if len(complete_results) != 1:
            raise ValueError('No service found: %s'
                             % service_id)

        provider_details_result = complete_results[0]['provider_details'] or {}
        results = {}
        for provider_name in provider_details_result:
            provider_detail_dict = json.loads(
                provider_details_result[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get("access_urls", [])
            status = provider_detail_dict.get("status", u'creating')
            domains_certificate_status = (
                provider_detail_dict.get('domains_certificate_status', {}))
            error_info = provider_detail_dict.get("error_info", None)
            error_message = provider_detail_dict.get("error_message", None)
            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                status=status,
                domains_certificate_status=domains_certificate_status,
                error_info=error_info,
                error_message=error_message)
            results[provider_name] = provider_detail_obj
        return results

    def get_service_details_by_domain_name(self, domain_name, project_id=None):
        """get_provider_details_by_domain_name.

        :param domain_name
        :param project_id
        :returns Provider details
        """

        LOG.info("Getting details of service having domain: '{0}'".format(
            domain_name))
        args = {
            'domain_name': domain_name.lower()
        }
        stmt = query.SimpleStatement(
            CQL_SEARCH_BY_DOMAIN,
            consistency_level=self._driver.consistency_level)
        result_set = self.session.execute(stmt, args)
        complete_results = list(result_set)
        # If there is not service with this domain
        # return None
        details = None
        for r in complete_results:
            proj_id = r.get('project_id')
            if project_id and proj_id != project_id:
                raise ValueError("Domain: {0} not "
                                 "present under "
                                 "project_id: {1}".format(domain_name,
                                                          project_id))
            service_id = r.get('service_id')
            details = self.get_service(proj_id, service_id)
        return details

    def update_provider_details(self, project_id, service_id,
                                new_provider_details):
        """update_provider_details.

        :param project_id
        :param service_id
        :param new_provider_details
        """

        old_domain_names_provider_urls = []
        old_provider_details = self.get_provider_details(
            project_id,
            service_id
        )
        for provider_name in sorted(old_provider_details.keys()):
            the_provider_detail_dict = collections.OrderedDict()
            the_provider_detail_dict["id"] = (
                old_provider_details[provider_name].provider_service_id)
            the_provider_detail_dict["access_urls"] = (
                old_provider_details[provider_name].access_urls)
            for access_url in the_provider_detail_dict["access_urls"]:
                domain_name = access_url.get("domain", None)
                provider_url = access_url.get("provider_url", None)
                if domain_name and provider_url:
                    old_domain_names_provider_urls.append(
                        (domain_name, provider_url)
                    )

        provider_detail_dict = {}
        status = None
        new_domain_names_provider_urls = []
        for provider_name in sorted(new_provider_details.keys()):
            the_provider_detail_dict = collections.OrderedDict()
            the_provider_detail_dict["id"] = (
                new_provider_details[provider_name].provider_service_id)
            the_provider_detail_dict["access_urls"] = (
                new_provider_details[provider_name].access_urls)
            for access_url in the_provider_detail_dict["access_urls"]:
                domain_name = access_url.get("domain", None)
                provider_url = access_url.get("provider_url", None)
                if domain_name and provider_url:
                    new_domain_names_provider_urls.append(
                        (domain_name, provider_url)
                    )
            the_provider_detail_dict["status"] = (
                new_provider_details[provider_name].status)
            status = the_provider_detail_dict["status"]
            the_provider_detail_dict["name"] = (
                new_provider_details[provider_name].name)
            the_provider_detail_dict["domains_certificate_status"] = (
                new_provider_details[provider_name].domains_certificate_status.
                to_dict())
            the_provider_detail_dict["error_info"] = (
                new_provider_details[provider_name].error_info)
            the_provider_detail_dict["error_message"] = (
                new_provider_details[provider_name].error_message)
            provider_detail_dict[provider_name] = json.dumps(
                the_provider_detail_dict)

        args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id)),
            'provider_details': provider_detail_dict
        }
        # TODO(tonytan4ever): Not sure this returns a list or a single
        # dictionary.
        # Needs to verify after cassandra unittest framework has been added in
        # if a list, the return the first item of a list. if it is a dictionary
        # returns the dictionary
        stmt = query.SimpleStatement(
            CQL_UPDATE_PROVIDER_DETAILS,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, args)

        service_args = {
            'project_id': project_id,
            'service_id': uuid.UUID(str(service_id)),
            'status': status
        }

        stmt = query.SimpleStatement(
            CQL_SET_SERVICE_STATUS,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, service_args)

        if new_domain_names_provider_urls:
            for domain_name, provider_url in new_domain_names_provider_urls:
                provider_url_args = {
                    'domain_name': domain_name,
                    'provider_url': provider_url
                }

                stmt = query.SimpleStatement(
                    CQL_SET_PROVIDER_URL,
                    consistency_level=self._driver.consistency_level)
                self.session.execute(stmt, provider_url_args)

        # remove mapping for domains that were deleted during the update
        deleted_domains = (
            set(old_domain_names_provider_urls) -
            set(new_domain_names_provider_urls)
        )
        for domain_name, provider_url in deleted_domains:
            provider_url_args = {
                'domain_name': domain_name,
                'provider_url': provider_url
            }

            stmt = query.SimpleStatement(
                CQL_DELETE_PROVIDER_URL,
                consistency_level=self._driver.consistency_level)
            self.session.execute(stmt, provider_url_args)

    @staticmethod
    def format_result(result):
        """format_result.

        :param result
        :returns formatted result
        """
        service_id = result.get('service_id')
        project_id = result.get('project_id')
        name = result.get('service_name')

        flavor_id = result.get('flavor_id')
        origins = [json.loads(o) for o in result.get('origins', []) or []]
        domains = [json.loads(d) for d in result.get('domains', []) or []]
        restrictions = [json.loads(r)
                        for r in result.get('restrictions', []) or []]
        caching_rules = [json.loads(c) for c in result.get('caching_rules', [])
                         or []]
        log_delivery = json.loads(result.get('log_delivery', '{}') or '{}')
        operator_status = result.get('operator_status', 'enabled')

        # create models for each item
        origins = [
            origin.Origin(
                o['origin'],
                o.get('hostheadertype', 'domain'),
                o.get('hostheadervalue', None),
                o.get('port', 80),
                o.get('ssl', False), [
                    rule.Rule(
                        rule_i.get('name'),
                        request_url=rule_i.get('request_url'))
                    for rule_i in o.get(
                        'rules', [])]) for o in origins]

        domains = [domain.Domain(d['domain'], d.get('protocol', 'http'),
                                 d.get('certificate', None))
                   for d in domains]

        restrictions = [restriction.Restriction(
            r.get('name'),
            r.get('access', 'whitelist'),
            [rule.Rule(r_rule.get('name'),
                       referrer=r_rule.get('referrer'),
                       client_ip=r_rule.get('client_ip'),
                       geography=r_rule.get('geography'),
                       request_url=r_rule.get('request_url', "/*") or "/*")
             for r_rule in r['rules']])
            for r in restrictions]

        caching_rules = [cachingrule.CachingRule(
            caching_rule.get('name'),
            caching_rule.get('ttl'),
            [rule.Rule(rule_i.get('name'),
                       request_url=rule_i.get('request_url', '/*') or '/*')
             for rule_i in caching_rule['rules']])
            for caching_rule in caching_rules]

        log_delivery = ld.LogDelivery(log_delivery.get('enabled', False))

        # create the service object
        s = service.Service(service_id=service_id,
                            name=name,
                            domains=domains,
                            origins=origins,
                            flavor_id=flavor_id,
                            caching=caching_rules,
                            restrictions=restrictions,
                            log_delivery=log_delivery,
                            operator_status=operator_status,
                            project_id=project_id)

        # format the provider details
        provider_detail_results = result.get('provider_details') or {}
        provider_details_dict = {}
        for provider_name in provider_detail_results:
            provider_detail_dict = json.loads(
                provider_detail_results[provider_name])
            provider_service_id = provider_detail_dict.get('id', None)
            access_urls = provider_detail_dict.get('access_urls', [])
            status = provider_detail_dict.get('status', u'unknown')
            domains_certificate_status = (
                provider_detail_dict.get('domains_certificate_status', {}))
            error_message = provider_detail_dict.get('error_message', None)

            provider_detail_obj = provider_details.ProviderDetail(
                provider_service_id=provider_service_id,
                access_urls=access_urls,
                domains_certificate_status=domains_certificate_status,
                status=status,
                error_message=error_message)
            provider_details_dict[provider_name] = provider_detail_obj
        s.provider_details = provider_details_dict

        # return the service
        return s
