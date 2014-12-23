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
import uuid

from oslo.config import cfg
import pecan
from pecan import hooks

from poppy.common import errors
from poppy.common import uri
from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.pecan.models.request import service as req_service_model
from poppy.transport.pecan.models.response import link
from poppy.transport.pecan.models.response import service as resp_service_model
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import service
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule

LIMITS_OPTIONS = [
    cfg.IntOpt('max_services_per_page', default=20,
               help='Max number of services per page for list services'),
]

LIMITS_GROUP = 'drivers:transport:limits'


class ServiceAssetsController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    @pecan.expose()
    @decorators.validate(
        service_id=rule.Rule(
            helpers.is_valid_service_id(),
            helpers.abort_with_message)
    )
    def delete(self, service_id):
        purge_url = pecan.request.GET.get('url', None)
        purge_all = pecan.request.GET.get('all', False)
        purge_all = (
            True if purge_all and purge_all.lower() == 'true' else False)
        if purge_url is None and not purge_all:
            pecan.abort(400, detail='No purge url provided '
                        'when not purging all...')
        elif purge_all and purge_url is not None:
            pecan.abort(400, detail='Cannot provide all=true '
                                    'and a url at the same time')
        services_controller = self._driver.manager.services_controller
        try:
            services_controller.purge(self.project_id, service_id,
                                      purge_url)
        except LookupError as e:
            pecan.abort(404, detail=str(e))

        return pecan.Response(None, 202)


class ServicesController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self._conf = driver.conf
        self._conf.register_opts(LIMITS_OPTIONS, group=LIMITS_GROUP)
        self.limits_conf = self._conf[LIMITS_GROUP]
        self.max_services_per_page = self.limits_conf.max_services_per_page
        # Add assets controller here
        # need to initialize a nested controller with a parameter driver,
        # so added it in __init__ method.
        # see more in: http://pecan.readthedocs.org/en/latest/rest.html
        self.__class__.assets = ServiceAssetsController(driver)

    @pecan.expose('json')
    def get_all(self):
        marker = pecan.request.GET.get('marker', None)
        limit = pecan.request.GET.get('limit', 10)
        try:
            limit = int(limit)
            if limit <= 0:
                pecan.abort(400, detail=u'Limit should be greater than 0')
            if limit > self.max_services_per_page:
                error = u'Limit should be less than or equal to {0}'.format(
                    self.max_services_per_page)
                pecan.abort(400, detail=error)
        except ValueError:
            error = (u'Limit should be an integer greater than 0 and less'
                     u' or equal to {0}'.format(self.max_services_per_page))
            pecan.abort(400, detail=error)

        try:
            if marker:
                marker = str(uuid.UUID(marker))
        except ValueError:
            pecan.abort(400, detail="Marker must be a valid UUID")

        services_controller = self._driver.manager.services_controller
        service_resultset = services_controller.list(
            self.project_id, marker, limit)
        results = [
            resp_service_model.Model(s, self)
            for s in service_resultset]
        # TODO(obulpathi): edge case: when the total number of services is a
        # multiple of limit, the last batch has a non-null marker.
        links = []
        if len(results) > 0:
            links.append(
                link.Model(u'{0}/services?marker={1}&limit={2}'.format(
                    self.base_url,
                    results[-1]['id'],
                    limit),
                    'next'))

        return {
            'links': links,
            'services': results
        }

    @pecan.expose('json')
    @decorators.validate(
        service_id=rule.Rule(
            helpers.is_valid_service_id(),
            helpers.abort_with_message)
    )
    def get_one(self, service_id):
        services_controller = self._driver.manager.services_controller
        try:
            service_obj = services_controller.get(
                self.project_id, service_id)
        except ValueError:
            pecan.abort(404, detail='service %s could not be found' %
                        service_id)
        # convert a service model into a response service model
        return resp_service_model.Model(service_obj, self)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_schema(
                service.ServiceSchema.get_schema("service", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        services_controller = self._driver.manager.services_controller
        service_json_dict = json.loads(pecan.request.body.decode('utf-8'))
        service_obj = req_service_model.load_from_json(service_json_dict)
        service_id = service_obj.service_id
        try:
            services_controller.create(self.project_id, service_obj)
        except LookupError as e:  # error handler for no flavor
            pecan.abort(400, detail=str(e))
        except ValueError as e:  # error handler for existing service name
            pecan.abort(400, detail=str(e))
        service_url = str(
            uri.encode(u'{0}/v1.0/services/{1}'.format(
                pecan.request.host_url,
                service_id)))

        return pecan.Response(None, 202, headers={"Location": service_url})

    @pecan.expose('json')
    @decorators.validate(
        service_id=rule.Rule(
            helpers.is_valid_service_id(),
            helpers.abort_with_message)
    )
    def delete(self, service_id):
        services_controller = self._driver.manager.services_controller
        try:
            services_controller.delete(self.project_id, service_id)
        except LookupError as e:
            pecan.abort(404, detail=str(e))

        return pecan.Response(None, 202)

    @pecan.expose('json')
    @decorators.validate(
        service_id=rule.Rule(
            helpers.is_valid_service_id(),
            helpers.abort_with_message),
        request=rule.Rule(
            helpers.json_matches_schema(
                service.ServiceSchema.get_schema("service", "PATCH")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def patch_one(self, service_id):
        service_json_dict = json.loads(pecan.request.body.decode('utf-8'))

        # TODO(obulpathi): remove these restrictions, once cachingrule and
        # restrictions models are implemented is implemented
        if 'caching' in service_json_dict:
            pecan.abort(400, detail='This operation is yet not supported')
        elif 'restrictions' in service_json_dict:
            pecan.abort(400, detail='This operation is yet not supported')

        # if service_json is empty, abort
        if not service_json_dict:
            pecan.abort(400, detail='No details provided to update')

        services_controller = self._driver.manager.services_controller
        service_updates = req_service_model.load_from_json(service_json_dict)

        try:
            services_controller.update(
                self.project_id, service_id, service_updates)
        except ValueError as e:
            pecan.abort(404, detail='service could not be found')
        except errors.ServiceStatusNotDeployed as e:
            pecan.abort(400, detail=str(e))
        except Exception as e:
            pecan.abort(400, detail=str(e))

        service_url = str(
            uri.encode(u'{0}/v1.0/services/{1}'.format(
                pecan.request.host_url,
                service_id)))

        return pecan.Response(None, 202, headers={"Location": service_url})
