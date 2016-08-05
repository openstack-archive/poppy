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
import random
import uuid

import jsonpatch
from oslo_context import context as context_utils
from oslo_log import log

from poppy.common import errors
from poppy.distributed_task.taskflow.flow import create_service
from poppy.distributed_task.taskflow.flow import delete_service
from poppy.distributed_task.taskflow.flow import purge_service
from poppy.distributed_task.taskflow.flow import update_service
from poppy.distributed_task.taskflow.flow import update_service_state
from poppy.manager import base
from poppy.model.helpers import cachingrule
from poppy.model.helpers import rule
from poppy.model import service
from poppy.model import ssl_certificate
from poppy.transport.validators import helpers as validators
from poppy.transport.validators.schemas import service as service_schema

LOG = log.getLogger(__name__)

DNS_GROUP = 'driver:dns'
PROVIDER_GROUP = 'drivers:provider'


class DefaultServicesController(base.ServicesController):

    """Default Services Controller."""

    def __init__(self, manager):
        super(DefaultServicesController, self).__init__(manager)

        self.storage_controller = self._driver.storage.services_controller
        self.ssl_certificate_storage = (
            self._driver.storage.certificates_controller
        )
        self.flavor_controller = self._driver.storage.flavors_controller
        self.dns_controller = self._driver.dns.services_controller
        self.distributed_task_controller = (
            self._driver.distributed_task.services_controller)

        self.dns_conf = self.driver.conf[DNS_GROUP]
        self.provider_conf = self.driver.conf[PROVIDER_GROUP]

    def determine_sleep_times(self):

        determined_sleep_time = \
            random.randrange(self.dns_conf.min_backoff_range,
                             self.dns_conf.max_backoff_range)

        backoff = [(2 ** i) * determined_sleep_time for i in
                   range(0, self.dns_conf.retries)]

        return backoff

    def _get_provider_details(self, project_id, service_id):
        try:
            provider_details = self.storage_controller.get_provider_details(
                project_id,
                service_id)
        except Exception:
            raise LookupError(u'Service {0} does not exist'.format(
                service_id))
        return provider_details

    def get_service_by_domain_name(self, domain_name):
        try:
            service_details = self.storage_controller\
                .get_service_details_by_domain_name(domain_name)
            if service_details is None:
                # as per latest change, get_service_details_by_domain_name
                # will return None if the service_details can not be found
                # for this domain
                raise LookupError
        except Exception:
            raise LookupError(u'Domain {0} does not exist'.format(
                domain_name))
        return service_details

    def get_services_by_status(self, status):

        services_project_ids = \
            self.storage_controller.get_services_by_status(status)

        return services_project_ids

    def get_domains_by_provider_url(self, provider_url):

        domains = \
            self.storage_controller.get_domains_by_provider_url(provider_url)

        return domains

    def _append_defaults(self, service_json, operation='create'):
        # default origin rule
        for origin in service_json.get('origins', []):
            if origin.get('rules') is None:
                # add a rules section
                origin['rules'] = []

            if origin.get('rules') == []:
                # add the /* default request_url rule
                default_rule = rule.Rule(
                    name="default",
                    request_url='/*')
                origin['rules'].append(default_rule.to_dict())
        if operation == 'create':
            # default caching rule
            if not service_json.get('caching'):
                # add the /* default request_url rule
                default_rule = rule.Rule(
                    name="default",
                    request_url='/*')
                default_ttl = self.provider_conf.default_cache_ttl
                default_cache = cachingrule.CachingRule(name='default',
                                                        ttl=default_ttl,
                                                        rules=[default_rule])
                service_json['caching'] = [default_cache.to_dict()]

        for caching_entry in service_json.get('caching', []):
            if caching_entry.get('rules') is None:
                # add a rules section
                caching_entry['rules'] = []
            if caching_entry.get('rules') == []:
                # add the /* default request_url rule
                default_rule = rule.Rule(
                    name="default",
                    request_url='/*')
                caching_entry['rules'].append(default_rule.to_dict())

    def get_services(self, project_id, marker=None, limit=None):
        """Get a list of services.

        :param project_id
        :param marker
        :param limit
        :return list
        """
        return self.storage_controller.get_services(project_id, marker, limit)

    def get_service(self, project_id, service_id):
        """get.

        :param project_id
        :param service_id
        :return controller
        """
        return self.storage_controller.get_service(project_id, service_id)

    def create_service(self, project_id, auth_token, service_json):
        """create.

        :param project_id
        :param auth_token
        :param service_json
        :raises LookupError, ValueError
        """
        try:
            flavor = self.flavor_controller.get(service_json.get('flavor_id'))
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        # add any default rules so its explicitly defined
        self._append_defaults(service_json, operation='create')

        # convert to an object
        service_obj = service.Service.init_from_dict(project_id, service_json)
        service_id = service_obj.service_id

        # validate the service
        service_json = service_obj.to_dict()
        schema = service_schema.ServiceSchema.get_schema("service", "POST")
        validators.is_valid_service_configuration(service_json, schema)

        service_limit = self.storage_controller.get_service_limit(project_id)
        service_count = self.storage_controller.get_service_count(project_id)

        services_delete_in_progress = self.storage_controller.\
            get_services_by_status('delete_in_progress')

        services_delete_count = len(services_delete_in_progress)

        # Check that the number of deleted services is less
        # than the total number of existing services for the project.
        # Adjust the service count removing delete_in_progress
        # services.
        service_count -= (
            services_delete_count
            if 0 < services_delete_count < service_count else 0
        )
        # service_count should always be a >= 0.

        if service_count >= service_limit:
            raise errors.ServicesOverLimit('Maximum Services '
                                           'Limit of {0} '
                                           'reached!'.format(service_limit))

        if any([domain for domain in service_obj.domains
                if domain.certificate == "shared"]):
            try:
                store = str(uuid.uuid4()).replace('-', '_')
                service_obj = self._shard_retry(project_id,
                                                service_obj,
                                                store=store)
            except errors.SharedShardsExhausted as e:
                raise e
            except ValueError as e:
                raise e

        try:
            self.storage_controller.create_service(project_id, service_obj)
        except ValueError as e:
            raise e

        providers = [p.provider_id for p in flavor.providers]
        kwargs = {
            'providers_list_json': json.dumps(providers),
            'project_id': project_id,
            'auth_token': auth_token,
            'service_id': service_id,
            'time_seconds': self.determine_sleep_times(),
            'context_dict': context_utils.get_current().to_dict()
        }

        self.distributed_task_controller.submit_task(
            create_service.create_service, **kwargs)

        return service_obj

    def update_service(self, project_id, service_id,
                       auth_token, service_updates, force_update=False):
        """update.

        :param project_id
        :param service_id
        :param auth_token
        :param service_updates
        :param force_update
        :raises LookupError, ValueError
        """
        # get the current service object
        try:
            service_old = self.storage_controller.get_service(
                project_id,
                service_id
            )
        except ValueError:
            raise errors.ServiceNotFound("Service not found")

        if service_old.operator_status == u'disabled':
            raise errors.ServiceStatusDisabled(
                u'Service {0} is disabled'.format(service_id))

        if (
            service_old.status not in [u'deployed', u'failed'] and
            force_update is False
        ):
            raise errors.ServiceStatusNeitherDeployedNorFailed(
                u'Service {0} neither deployed nor failed'.format(service_id))

        # Fixing the operator_url domain for ssl
        # for schema validation
        existing_shared_domains = {}
        for domain in service_old.domains:
            if domain.protocol == 'https' and domain.certificate == 'shared':
                customer_domain = domain.domain.split('.')[0]
                existing_shared_domains[customer_domain] = domain.domain
                domain.domain = customer_domain

            # old domains need to bind as well
            elif domain.certificate == 'san':
                cert_for_domain = (
                    self.ssl_certificate_storage.get_certs_by_domain(
                        domain.domain,
                        project_id=project_id,
                        flavor_id=service_old.flavor_id,
                        cert_type=domain.certificate))
                if cert_for_domain == []:
                    cert_for_domain = None
                domain.cert_info = cert_for_domain

        service_old_json = json.loads(json.dumps(service_old.to_dict()))

        # remove fields that cannot be part of PATCH
        del service_old_json['service_id']
        del service_old_json['status']
        del service_old_json['operator_status']
        del service_old_json['provider_details']

        for domain in service_old_json['domains']:
            if 'cert_info' in domain:
                del domain['cert_info']

        service_new_json = jsonpatch.apply_patch(
            service_old_json, service_updates)

        # add any default rules so its explicitly defined
        self._append_defaults(service_new_json, operation='update')

        # validate the updates
        schema = service_schema.ServiceSchema.get_schema("service", "POST")
        validators.is_valid_service_configuration(service_new_json, schema)

        try:
            self.flavor_controller.get(service_new_json['flavor_id'])
        # raise a lookup error if the flavor is not found
        except LookupError as e:
            raise e

        # must be valid, carry on
        service_new_json['service_id'] = service_old.service_id
        service_new = service.Service.init_from_dict(project_id,
                                                     service_new_json)

        store = str(uuid.uuid4()).replace('-', '_')
        service_new.provider_details = service_old.provider_details

        # fixing the old and new shared ssl domains in service_new
        for domain in service_new.domains:
            if domain.protocol == 'https':
                if domain.certificate == 'shared':
                    customer_domain = domain.domain.split('.')[0]
                    # if this domain is from service_old
                    if customer_domain in existing_shared_domains:
                        domain.domain = existing_shared_domains[
                            customer_domain
                        ]
                    else:
                        domain.domain = self._pick_shared_ssl_domain(
                            customer_domain,
                            service_new.service_id,
                            store)
                elif domain.certificate == 'san':
                    cert_for_domain = (
                        self.ssl_certificate_storage.get_certs_by_domain(
                            domain.domain,
                            project_id=project_id,
                            flavor_id=service_new.flavor_id,
                            cert_type=domain.certificate))
                    if cert_for_domain == []:
                        cert_for_domain = None
                    domain.cert_info = cert_for_domain

                    # retrofit the access url info into
                    # certificate_info table
                    # Note(tonytan4ever): this is for backward
                    # compatibility
                    if domain.cert_info is None and \
                            service_new.provider_details is not None:
                        # Note(tonytan4ever): right now we assume
                        # only one provider per flavor, that's
                        # why we use values()[0]
                        access_url_for_domain = (
                            service_new.provider_details.values()[0].
                            get_domain_access_url(domain.domain))
                        if access_url_for_domain is not None:
                            providers = (
                                self.flavor_controller.get(
                                    service_new.flavor_id).providers
                            )
                            san_cert_url = access_url_for_domain.get(
                                'provider_url')
                            # Note(tonytan4ever): stored san_cert_url
                            # for two times, that's intentional
                            # a little extra info does not hurt
                            new_cert_detail = {
                                providers[0].provider_id.title():
                                json.dumps(dict(
                                    cert_domain=san_cert_url,
                                    extra_info={
                                        'status': 'deployed',
                                        'san cert': san_cert_url,
                                        'created_at': str(
                                            datetime.datetime.now())
                                    }
                                ))
                            }
                            new_cert_obj = ssl_certificate.SSLCertificate(
                                service_new.flavor_id,
                                domain.domain,
                                'san',
                                project_id,
                                new_cert_detail
                            )
                            self.ssl_certificate_storage.create_certificate(
                                project_id,
                                new_cert_obj
                            )
                            # deserialize cert_details dict
                            new_cert_obj.cert_details[
                                providers[0].provider_id.title()] = json.loads(
                                new_cert_obj.cert_details[
                                    providers[0].provider_id.title()]
                            )
                            domain.cert_info = new_cert_obj

        if hasattr(self, store):
            delattr(self, store)

        # check if the service domain names already exist
        # existing shared domains do not count!
        for d in service_new.domains:
            if self.storage_controller.domain_exists_elsewhere(
                    d.domain,
                    service_id) is True and \
                    d.domain not in existing_shared_domains.values():
                raise ValueError(
                    "Domain {0} has already been taken".format(d.domain))

        # set status in provider details to u'update_in_progress'
        provider_details = service_old.provider_details
        for provider in provider_details:
            provider_details[provider].status = u'update_in_progress'
        service_new.provider_details = provider_details
        self.storage_controller.update_service(
            project_id,
            service_id,
            service_new
        )

        kwargs = {
            'project_id': project_id,
            'service_id': service_id,
            'auth_token': auth_token,
            'service_old': json.dumps(service_old.to_dict()),
            'service_obj': json.dumps(service_new.to_dict()),
            'time_seconds': self.determine_sleep_times(),
            'context_dict': context_utils.get_current().to_dict()
        }

        self.distributed_task_controller.submit_task(
            update_service.update_service, **kwargs)

        return

    def services_limit(self, project_id, limit):
        self.storage_controller.set_service_limit(
            project_id=project_id,
            project_limit=limit)

    def set_service_provider_details(self, project_id, service_id,
                                     auth_token, status):
        old_service = self.storage_controller.get_service(
            project_id,
            service_id
        )

        if (
            old_service.status == 'create_in_progress' and
            old_service.provider_details == {}
        ):
            self.update_service(
                project_id, service_id, auth_token, [], force_update=True)
            return 202
        self.storage_controller.set_service_provider_details(
            project_id,
            service_id,
            status
        )
        return 201

    def get_services_limit(self, project_id):
        limit = self.storage_controller.get_service_limit(
            project_id=project_id)

        return {
            'limit': limit
        }

    def _action_per_service_obj(self, project_id, action, service_obj):

        kwargs = {
            'project_id': project_id,
            'service_obj': json.dumps(service_obj.to_dict()),
            'time_seconds': self.determine_sleep_times(),
            'context_dict': context_utils.get_current().to_dict()
        }

        try:
            if action == 'delete':
                LOG.info('Deleting  service: %s, project_id: %s' % (
                    service_obj.service_id, project_id))
                self.delete_service(project_id, service_obj.service_id)
            elif action == 'enable':
                LOG.info('Enabling  service: %s, project_id: %s' % (
                    service_obj.service_id, project_id))
                kwargs['state'] = 'enabled'
                self.distributed_task_controller.submit_task(
                    update_service_state.enable_service, **kwargs)
            elif action == 'disable':
                LOG.info('Disabling  service: %s, project_id: %s' % (
                    service_obj.service_id, project_id))
                kwargs['state'] = 'disabled'
                self.distributed_task_controller.submit_task(
                    update_service_state.disable_service, **kwargs)
        except Exception as e:
            # If one service's action failed, we log it and not
            # impact other services' action
            LOG.warning('Perform action %s on service: %s,'
                        ' project_id: %s failed, reason: %s' % (
                            action,
                            service_obj.service_id,
                            project_id,
                            str(e)))

    def services_action(self, project_id, action, domain=None):
        """perform action on services

        :param project_id
        :param action
        :param domain

        :raises ValueError
        """

        # list all the services of for this project_id
        # 10 per batch

        if domain:
            service_obj = self.get_service_by_domain_name(domain_name=domain)
            self._action_per_service_obj(project_id=service_obj.project_id,
                                         action=action,
                                         service_obj=service_obj)
            return

        marker = None
        service_batch = self.storage_controller.get_services(
            project_id,
            marker,
            10
        )
        while len(service_batch) > 0:
            marker = service_batch[-1].service_id
            # process previous batch
            for service_obj in service_batch:
                self._action_per_service_obj(project_id=project_id,
                                             action=action,
                                             service_obj=service_obj)
            service_batch = self.storage_controller.get_services(
                project_id,
                marker,
                10
            )

        return

    def delete_service(self, project_id, service_id):
        """delete.

        :param project_id
        :param service_id
        :raises LookupError
        """
        service_obj = self.storage_controller.get_service(
            project_id, service_id)

        # get provider details for this service
        provider_details = self._get_provider_details(project_id, service_id)

        # change each provider detail's status to delete_in_progress
        for provider in service_obj.provider_details:
            service_obj.provider_details[provider].status = (
                u'delete_in_progress')

        self.storage_controller.update_service(
            project_id,
            service_id,
            service_obj
        )

        kwargs = {
            "provider_details": json.dumps(
                dict([(k, v.to_dict()) for k, v in provider_details.items()])),
            "project_id": project_id,
            "service_id": service_id,
            'time_seconds': self.determine_sleep_times(),
            'context_dict': context_utils.get_current().to_dict()
        }

        self.distributed_task_controller.submit_task(
            delete_service.delete_service, **kwargs)

        return

    def purge(self, project_id, service_id, hard=False, purge_url=None):
        """If purge_url is none, all content of this service will be purge."""
        try:
            service_obj = self.storage_controller.get_service(
                project_id,
                service_id
            )
        except ValueError as e:
            # This except is hit when service object does not exist
            raise LookupError(str(e))

        if service_obj.status not in [u'deployed']:
            raise errors.ServiceStatusNotDeployed(
                u'Service {0} is not deployed.'.format(service_id))

        provider_details = self._get_provider_details(project_id, service_id)

        # change each provider detail's status to
        # cache_invalidation_in_progress if its a soft invalidation,
        # i.e hard is set to False
        if not hard:
            for provider in service_obj.provider_details:
                service_obj.provider_details[provider].status = (
                    u'update_in_progress')

        self.storage_controller.update_service(
            project_id,
            service_id,
            service_obj
        )

        # possible validation of purge url here...
        kwargs = {
            'service_obj': json.dumps(service_obj.to_dict()),
            'provider_details': json.dumps(
                dict([(k, v.to_dict()) for k, v in provider_details.items()])),
            'project_id': project_id,
            'hard': json.dumps(hard),
            'service_id': service_id,
            'purge_url': str(purge_url),
            'context_dict': context_utils.get_current().to_dict()
        }

        self.distributed_task_controller.submit_task(
            purge_service.purge_service, **kwargs)

        return

    def _generate_shared_ssl_domain(self, domain_name, store):
        try:
            if not hasattr(self, store):
                gen_store = {
                    domain_name:
                        self.dns_controller.generate_shared_ssl_domain_suffix()
                }
                setattr(self, store, gen_store)
            uuid_store = getattr(self, store)
            if domain_name not in uuid_store:
                uuid_store[domain_name] = \
                    self.dns_controller.generate_shared_ssl_domain_suffix()
                setattr(self, store, uuid_store)
            return '.'.join([domain_name,
                             next(uuid_store[domain_name])])
        except StopIteration:
            delattr(self, store)
            raise errors.SharedShardsExhausted('Domain {0} '
                                               'has already '
                                               'been '
                                               'taken'.format(domain_name))

    def _pick_shared_ssl_domain(self, domain, service_id, store):
        shared_ssl_domain = self._generate_shared_ssl_domain(
            domain,
            store)
        while self.storage_controller.domain_exists_elsewhere(
                shared_ssl_domain,
                service_id):
            shared_ssl_domain = self._generate_shared_ssl_domain(
                domain,
                store)
        return shared_ssl_domain

    def _shard_retry(self, project_id, service_obj, store=None):
            # deal with shared ssl domains
        try:
            for domain in service_obj.domains:
                if domain.protocol == 'https' \
                        and domain.certificate == 'shared':
                    shared_domain = domain.domain.split('.')[0]
                    shared_ssl_domain = self._pick_shared_ssl_domain(
                        shared_domain,
                        service_obj.service_id,
                        store)
                    domain.domain = shared_ssl_domain

            if hasattr(self, store):
                delattr(self, store)
            return service_obj

        except ValueError as e:
            if hasattr(self, store):
                delattr(self, store)
            raise ValueError(str(e))

    def migrate_domain(self, project_id, service_id, domain_name, new_cert,
                       cert_status='deployed'):
        dns_controller = self.dns_controller
        storage_controller = self.storage_controller

        try:
            # Update CNAME records and provider_details in cassandra
            provider_details = storage_controller.get_provider_details(
                project_id, service_id)
        except ValueError as e:
            # If service is not found
            LOG.warning('Migrating domain failed: Service {0} could not '
                        'be found. Error message: {1}'.format(service_id, e))
            raise errors.ServiceNotFound(e)

        for provider in provider_details:
            provider_details[provider].domains_certificate_status.\
                set_domain_certificate_status(domain_name, cert_status)

            # Currently there's only one flavor, and thus expect one result
            # from the query below. Once additional flavors are added, a
            # query for the service object rather than provider details only
            # should provide the flavor id to use in the query below
            cert_obj = self.ssl_certificate_storage.get_certs_by_domain(
                domain_name,
                project_id=project_id,
                cert_type='san'
            )

            if cert_obj != []:
                # cert was found, update the cert status
                cert_details = cert_obj.cert_details
                cert_details[provider]['extra_info']['status'] = cert_status
                cert_details[provider] = json.dumps(cert_details[provider])

                storage_controller.update_cert_info(
                    cert_obj.domain_name,
                    cert_obj.cert_type,
                    cert_obj.flavor_id,
                    cert_details
                )

            for url in provider_details[provider].access_urls:
                if url.get('domain') == domain_name:
                    if 'operator_url' in url:
                        access_url = url['operator_url']
                        dns_controller.modify_cname(access_url, new_cert)
                        url['provider_url'] = new_cert
                        break
            else:
                links = {}
                link_key_tuple = (domain_name, 'san')
                links[link_key_tuple] = new_cert
                created_dns_link = dns_controller._create_cname_records(links)
                new_url = {
                    'domain': domain_name,
                    'operator_url': (
                        created_dns_link[link_key_tuple]['operator_url']),
                    'provider_url': new_cert
                }
                provider_details[provider].access_urls.append(new_url)

            storage_controller.update_provider_details(
                project_id,
                service_id,
                provider_details
            )
