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

from oslo.config import cfg
import pecan

from poppy.common import uri
from poppy.transport.pecan.controllers import base
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


class ServiceAssetsController(base.Controller):
    pass


class ServicesController(base.Controller):

    # TODO(tonytan4ever): Add assets controller for purge, etc
    # assets = ServiceAssetsController()

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)
        self._conf = driver.conf
        self._conf.register_opts(LIMITS_OPTIONS, group=LIMITS_GROUP)
        self.limits_conf = self._conf[LIMITS_GROUP]
        self.max_services_per_page = self.limits_conf.max_services_per_page

    @pecan.expose('json')
    def get_all(self):
        marker = pecan.request.GET.get('marker', '')
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

        services_controller = self._driver.manager.services_controller
        service_resultset = services_controller.list(
            self.project_id, marker, limit)
        results = [
            resp_service_model.Model(s, pecan.request)
            for s in service_resultset]
        # TODO(obulpathi): edge case: when the total number of services is a
        # multiple of limit, the last batch has a non-null marker.
        links = []
        if len(results) > 0:
            links.append(
                link.Model(u'{0}/services?marker={1}&limit={2}'.format(
                    self.base_url, results[-1]['name'], limit),
                    'next'))

        return {
            'links': links,
            'services': results
        }

    @pecan.expose('json')
    def get_one(self, service_name):
        services_controller = self._driver.manager.services_controller
        try:
            service_obj = services_controller.get(
                self.project_id, service_name)
        except ValueError:
            pecan.abort(404, detail='service %s is not found' %
                        service_name)
        # convert a service model into a response service model
        return resp_service_model.Model(service_obj, pecan.request)

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
        service_name = service_json_dict.get("name", None)
        try:
            services_controller.create(self.project_id, service_obj, service_json_dict)
        except LookupError as e:  # error handler for no flavor
            pecan.abort(400, detail=str(e))
        except ValueError as e:  # error handler for existing service name
            pecan.abort(400, detail=str(e))
        service_url = str(
            uri.encode(u'{0}/v1.0/services/{1}'.format(
                pecan.request.host_url,
                service_name)))
        pecan.response.status = 202
        pecan.response.headers["Location"] = service_url

    @pecan.expose('json')
    def delete(self, service_name):
        services_controller = self._driver.manager.services_controller
        try:
            services_controller.delete(self.project_id, service_name)
        except LookupError as e:
            pecan.abort(404, detail=str(e))
        pecan.response.status = 202

    @pecan.expose('json')
    @decorators.validate(
        service_name=rule.Rule(
            helpers.is_valid_service_name(),
            helpers.abort_with_message),
        request=rule.Rule(
            helpers.json_matches_schema(
                service.ServiceSchema.get_schema("service", "PATCH")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def patch_one(self, service_name):
        services_controller = self._driver.manager.services_controller
        service_json = json.loads(pecan.request.body.decode('utf-8'))
        # TODO(tonytan4ever): convert service_json into a partial service model
        # under poppy.models.helpers.service.py
        # and pass service_json to update
        return services_controller.update(self.project_id, service_name,
                                          service_json)
