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

from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.pecan.models.request import ssl_certificate
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import ssl_certificate\
    as ssl_certificate_validation
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule


class SSLCertificateController(base.Controller, hooks.HookController):

    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                ssl_certificate_validation.SSLCertificateSchema.get_schema(
                    "ssl_certificate",
                    "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        ssl_certificate_controller = (
            self._driver.manager.ssl_certificate_controller)

        certificate_info_dict = json.loads(pecan.request.body.decode('utf-8'))

        try:
            cert_obj = ssl_certificate.load_from_json(certificate_info_dict)
            ssl_certificate_controller.create_ssl_certificate(self.project_id,
                                                              cert_obj)
        except LookupError as e:
            pecan.abort(400, detail='Provisioning ssl certificate failed. '
                        'Reason: %s' % str(e))
        except ValueError as e:
            pecan.abort(400, detail='Provisioning ssl certificate failed. '
                        'Reason: %s' % str(e))

        return pecan.Response(None, 202)
