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
from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.pecan.models.response import service as resp_service_model
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import domain_migration
from poppy.transport.validators.schemas import service_action
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

        if not helpers.is_valid_domain_name(domain_name):
            pecan.abort(400, detail='Domain {0} is not valid'.format(
                domain_name))

        # Akamai specific suffix:
        if not new_cert.endswith("edgekey.net"):
            new_cert = new_cert + ".edgekey.net"

        try:
            self._driver.manager.services_controller.migrate_domain(
                project_id, service_id, domain_name, new_cert)
        except errors.ServiceNotFound:
            pecan.abort(404, detail='Service {0} could not be found'.format(
                service_id))
        except LookupError:
            pecan.abort(404, detail='Domain {0} could not be found'.format(
                domain_name))

        return pecan.Response(None, 202)


class AkamaiController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AkamaiController, self).__init__(driver)
        self.__class__.service = DomainMigrationController(driver)


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
        project_limit = service_state_json.get('limit', None)

        services_controller = self._driver.manager.services_controller

        try:
            services_controller.services_action(project_id,
                                                service_action,
                                                project_limit)
        except Exception as e:
            pecan.abort(404, detail=(
                        'Services action {0} on tenant: {1} failed, '
                        'Reason: {2}'.format(service_action,
                                             project_id, str(e))))

        return pecan.Response(None, 202)


class AdminServiceController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AdminServiceController, self).__init__(driver)
        self.__class__.action = OperatorServiceActionController(driver)


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


class AdminController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AdminController, self).__init__(driver)
        self.__class__.services = AdminServiceController(driver)
        self.__class__.provider = ProviderController(driver)
        self.__class__.domains = DomainController(driver)
