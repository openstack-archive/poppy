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
import pecan
from pecan import hooks

from poppy.common import errors
from poppy.common import util
from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.pecan.models.response import service as resp_service_model
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import background_jobs
from poppy.transport.validators.schemas import domain_migration
from poppy.transport.validators.schemas import service_action
from poppy.transport.validators.schemas import service_limit
from poppy.transport.validators.schemas import service_status
from poppy.transport.validators.schemas import ssl_certificate
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule


class DomainMigrationController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(DomainMigrationController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                domain_migration.DomainMigrationServiceSchema.get_schema(
                    "domain_migration", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        request_json = json.loads(pecan.request.body.decode('utf-8'))
        project_id = request_json.get('project_id', None)
        service_id = request_json.get('service_id', None)
        domain_name = request_json.get('domain_name', None)
        new_cert = request_json.get('new_cert', None)
        cert_status = request_json.get('cert_status', 'deployed')

        if not helpers.is_valid_domain_name(domain_name):
            pecan.abort(400, detail='Domain {0} is not valid'.format(
                domain_name))

        # Akamai specific suffix:
        if not new_cert.endswith("edgekey.net"):
            new_cert = new_cert + ".edgekey.net"

        try:
            self._driver.manager.services_controller.migrate_domain(
                project_id, service_id, domain_name, new_cert, cert_status)
        except errors.ServiceNotFound:
            pecan.abort(404, detail='Service {0} could not be found'.format(
                service_id))
        except (LookupError, ValueError):
            pecan.abort(404, detail='Domain {0} could not be found'.format(
                domain_name))

        return pecan.Response(None, 202)


class BackgroundJobController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(BackgroundJobController, self).__init__(driver)
        self.__class__.san_mapping = AkamaiSanMappingListController(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                background_jobs.BackgroundJobSchema.get_schema(
                    "background_jobs", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        request_json = json.loads(pecan.request.body.decode('utf-8'))
        job_type = request_json.pop('job_type')

        sent = []
        ignored = []

        try:
            sent, ignored = self._driver.manager.background_job_controller.\
                post_job(job_type, request_json)
        except NotImplementedError as e:
            pecan.abort(400, str(e))

        return pecan.Response(
            json_body={
                "sent": sent,
                "ignored": ignored
            },
            status=202,
        )


class AkamaiSanMappingListController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(AkamaiSanMappingListController, self).__init__(driver)

        self.manager = self._driver.manager

    @pecan.expose('json')
    def get_all(self):
        try:
            return (
                self.manager.background_job_controller.get_san_mapping_list())
        except Exception as e:
            pecan.abort(404, str(e))

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                ssl_certificate.SSLCertificateSchema.get_schema(
                    "san_mapping_list", "PUT")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def put(self):
        """The input of the queue data must be a list of dictionaries:

        (after json loaded)
        [
          { "domain_name": <domain_name>,
            "san_cert_name": <san_cert_name>
          }
        ]
        """
        try:
            san_mapping_list = json.loads(pecan.request.body.decode('utf-8'))
            res, deleted = (
                self.manager.background_job_controller.
                put_san_mapping_list(san_mapping_list))
            # queue is the new queue, and deleted is deleted items
            return {"queue": res,  "deleted": deleted}
        except Exception as e:
            pecan.abort(400, str(e))


class AkamaiRetryListController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(AkamaiRetryListController, self).__init__(driver)

    @pecan.expose('json')
    def get_all(self):
        retry_list = None
        try:
            retry_list = (
                self._driver.manager.ssl_certificate_controller.
                get_san_retry_list())
        except Exception as e:
            pecan.abort(404, str(e))

        return retry_list

    @pecan.expose('json')
    def post(self):
        """Rerun retry-list mod-san requests."""
        sent, ignored = None, None
        try:
            sent, ignored = self._driver.manager.ssl_certificate_controller.\
                rerun_san_retry_list()
        except Exception as e:
            pecan.abort(404, str(e))

        return pecan.Response(
            json_body={"processing": sent, "failed_validation": ignored},
            status=202
        )

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                ssl_certificate.SSLCertificateSchema.get_schema(
                    "retry_list", "PUT")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def put(self):
        """The input of the queue data must be a list of dictionaries:

        (after json loaded)
        [
          { "domain_name": <domain_name>,
            "project_id": <project_id>,
            "flavor_id": <flavor_id> }
        ]

        """
        try:
            queue_data = json.loads(pecan.request.body.decode('utf-8'))
            res, deleted = (
                self._driver.manager.ssl_certificate_controller.
                update_san_retry_list(queue_data))
            # queue is the new queue, and deleted is deleted items
            return {"queue": res,  "deleted": deleted}
        except Exception as e:
            pecan.abort(400, str(e))


class AkamaiSanCertConfigController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    @pecan.expose('json')
    @decorators.validate(
        query=rule.Rule(
            helpers.is_valid_domain_by_name_or_akamai_setting(),
            helpers.abort_with_message))
    def get_one(self, query):

        if query == 'san_cert_hostname_limit':
            try:
                return (
                    self._driver.manager.ssl_certificate_controller.
                    get_san_cert_hostname_limit()
                )
            except Exception as e:
                pecan.abort(400, str(e))
        else:
            try:
                return (
                    self._driver.manager.ssl_certificate_controller.
                    get_san_cert_configuration(query)
                )
            except Exception as e:
                pecan.abort(400, str(e))

    @pecan.expose('json')
    @decorators.validate(
        query=rule.Rule(
            helpers.is_valid_domain_by_name_or_akamai_setting(),
            helpers.abort_with_message),
        request=rule.Rule(
            helpers.json_matches_service_schema(
                ssl_certificate.SSLCertificateSchema.get_schema(
                    "config", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self, query):
        request_json = json.loads(pecan.request.body.decode('utf-8'))

        if query == 'san_cert_hostname_limit':
            try:
                self._driver.manager.ssl_certificate_controller. \
                    set_san_cert_hostname_limit(request_json)

                return pecan.Response(None, 202)
            except Exception as e:
                pecan.abort(400, str(e))
        else:
            try:
                res = (
                    self._driver.manager.ssl_certificate_controller.
                    update_san_cert_configuration(query, request_json))
                return res
            except Exception as e:
                pecan.abort(400, str(e))


class AkamaiSSLCertificateController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(AkamaiSSLCertificateController, self).__init__(driver)
        self.__class__.retry_list = AkamaiRetryListController(driver)
        self.__class__.config = AkamaiSanCertConfigController(driver)


class AkamaiController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AkamaiController, self).__init__(driver)
        self.__class__.service = DomainMigrationController(driver)
        self.__class__.background_job = BackgroundJobController(driver)
        self.__class__.ssl_certificate = AkamaiSSLCertificateController(driver)


class ProviderController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(ProviderController, self).__init__(driver)
        self.__class__.akamai = AkamaiController(driver)


class OperatorServiceActionController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(OperatorServiceActionController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                service_action.ServiceActionSchema.get_schema(
                    "service_action", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):

        service_state_json = json.loads(pecan.request.body.decode('utf-8'))
        service_action = service_state_json.get('action', None)
        project_id = service_state_json.get('project_id', None)
        domain_name = service_state_json.get('domain', None)
        services_controller = self._driver.manager.services_controller

        try:
            services_controller.services_action(project_id,
                                                service_action,
                                                domain_name)

        except Exception as e:
            pecan.abort(404, detail=(
                        'Services action {0} on tenant: {1} failed, '
                        'Reason: {2}'.format(service_action,
                                             project_id, str(e))))

        return pecan.Response(None, 202)


class OperatorServiceLimitController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(OperatorServiceLimitController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                service_limit.ServiceLimitSchema.get_schema(
                    "service_limit", "PUT")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter),
        project_id=rule.Rule(
            helpers.is_valid_project_id(),
            helpers.abort_with_message)
    )
    def put(self, project_id):

        service_state_json = json.loads(pecan.request.body.decode('utf-8'))
        project_limit = service_state_json.get('limit', None)

        services_controller = self._driver.manager.services_controller

        try:
            services_controller.services_limit(project_id,
                                               project_limit)
        except Exception as e:
            pecan.abort(404, detail=(
                        'Services limit {0} on tenant: {1} failed, '
                        'Reason: {2}'.format(project_limit,
                                             project_id, str(e))))

        return pecan.Response(None, 201)

    @pecan.expose('json')
    @decorators.validate(
        project_id=rule.Rule(
            helpers.is_valid_project_id(),
            helpers.abort_with_message)
    )
    def get_one(self, project_id):
        services_controller = self._driver.manager.services_controller

        service_limits = services_controller.get_services_limit(
            project_id)

        return service_limits


class ServiceStatusController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(ServiceStatusController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                service_status.ServiceStatusSchema.get_schema(
                    "service_status", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter)
    )
    def post(self):

        service_state_json = json.loads(pecan.request.body.decode('utf-8'))
        project_id = service_state_json['project_id']
        service_id = service_state_json['service_id']
        status = service_state_json['status']
        services_controller = self._driver.manager.services_controller

        status_code = None
        try:
            status_code = services_controller.set_service_provider_details(
                project_id,
                service_id,
                self.auth_token,
                status
            )
        except Exception as e:
            pecan.abort(404, detail=(
                        'Setting state of service {0} on tenant: {1} '
                        'to {2} has failed, '
                        'Reason: {3}'.format(service_id,
                                             project_id,
                                             status,
                                             str(e))))

        return pecan.Response(None, status_code)


class AdminCertController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(AdminCertController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.is_valid_certificate_status(),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter)
    )
    def get(self):
        ssl_certificate_controller = (
            self._driver.manager.ssl_certificate_controller
        )

        call_args = getattr(pecan.request.context,
                            "call_args")
        status = call_args.pop('status')
        cert_domains = ssl_certificate_controller.get_certs_by_status(
            status)

        return pecan.Response(json_body=cert_domains, status=200)

    @pecan.expose('json')
    @decorators.validate(
        domain_name=rule.Rule(
            helpers.is_valid_domain_by_name(),
            helpers.abort_with_message
        ),
        request=rule.Rule(
            helpers.json_matches_service_schema(
                ssl_certificate.SSLCertificateSchema.get_schema(
                    "admin_cert_status",
                    "PATCH"
                )
            ),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter)
    )
    def patch_one(self, domain_name):

        ssl_certificate_controller = (
            self._driver.manager.ssl_certificate_controller
        )
        certificate_updates = json.loads(pecan.request.body.decode('utf-8'))[0]
        try:
            ssl_certificate_controller.update_certificate_status(
                domain_name,
                certificate_updates
            )
        except ValueError:
            pecan.abort(
                status_code=404,
                detail='Certificate could not be found for domain: {0}'.format(
                    domain_name
                )
            )
        except Exception as e:
            pecan.abort(status_code=400, detail=util.help_escape(str(e)))

        return pecan.Response(body=None, status=204)


class AdminServiceController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(AdminServiceController, self).__init__(driver)
        self.__class__.action = OperatorServiceActionController(driver)
        self.__class__.status = ServiceStatusController(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.is_valid_service_status(),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter)
    )
    def get(self):
        services_controller = self._driver.manager.services_controller

        call_args = getattr(pecan.request.context,
                            "call_args")
        status = call_args.pop('status')
        service_projectids = services_controller.get_services_by_status(
            status)

        return pecan.Response(json_body=service_projectids,
                              status=200)


class DomainController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(DomainController, self).__init__(driver)

        self._conf = driver.conf

    @pecan.expose('json')
    @decorators.validate(
        domain_name=rule.Rule(
            helpers.is_valid_domain_by_name(),
            helpers.abort_with_message)
    )
    def get_one(self, domain_name):
        services_controller = self._driver.manager.services_controller
        try:
            service_obj = services_controller.get_service_by_domain_name(
                domain_name)
        except LookupError:
            pecan.abort(404, detail='Domain %s cannot be found' %
                        domain_name)
        # convert a service model into a response service model
        return resp_service_model.Model(service_obj, self)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.is_valid_provider_url(),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter)
    )
    def get(self):
        services_controller = self._driver.manager.services_controller

        call_args = getattr(pecan.request.context,
                            "call_args")
        provider_url = call_args.pop('provider_url')
        domains = services_controller.get_domains_by_provider_url(
            provider_url)

        return pecan.Response(json_body=domains,
                              status=200)


class AdminController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AdminController, self).__init__(driver)
        self.__class__.services = AdminServiceController(driver)
        self.__class__.certificates = AdminCertController(driver)
        self.__class__.provider = ProviderController(driver)
        self.__class__.domains = DomainController(driver)
        self.__class__.limits = OperatorServiceLimitController(driver)
