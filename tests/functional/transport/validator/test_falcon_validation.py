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

import functools

from poppy.common import errors
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import service
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions
from poppy.transport.validators.stoplight import rule
from tests.functional.transport.validator import base


testing_schema = service.ServiceSchema.get_schema("service", "PUT")
request_fit_schema = functools.partial(
    helpers.with_schema_falcon,
    schema=testing_schema)


class DummyFalconEndpoint(object):
    # falcon style endpoint

    @decorators.validate(
        request=rule.Rule(
            request_fit_schema,
            lambda error_info: base.abort(404)
        ),
        response=rule.Rule(
            base.is_response(),
            lambda error_info: base.abort(404))
    )
    def get_falcon_style(self, request, response):
        return "Hello, World!"

    @decorators.validate(
        request=rule.Rule(request_fit_schema,
                          helpers.custom_abort_falcon),
        response=rule.Rule(base.is_response(),
                           helpers.custom_abort_falcon)
    )
    def get_falcon_style_custom_abort(self, request, response):
        return "Hello, World!"


class TestValidationFunctionsFalcon(base.BaseTestCase):

    def setUp(self):
        self.ep = DummyFalconEndpoint()
        super(TestValidationFunctionsFalcon, self).setUp()

    def test_with_schema(self):
        self.assertEqual(
            helpers.with_schema_falcon(
                base.fake_request_good,
                schema=testing_schema),
            None)
        with self.assertRaisesRegexp(exceptions.ValidationFailed, "domain"):
            helpers.with_schema_falcon(
                base.fake_request_bad_missing_domain,
                schema=testing_schema)
        with self.assertRaisesRegexp(exceptions.ValidationFailed,
                                     "Invalid JSON body in request"):
            helpers.with_schema_falcon(
                base.fake_request_bad_invalid_json_body,
                schema=testing_schema)

    def test_partial_with_schema(self):
        self.assertEqual(request_fit_schema(base.fake_request_good), None)
        with self.assertRaisesRegexp(exceptions.ValidationFailed, "domain"):
            request_fit_schema(base.fake_request_bad_missing_domain)
        with self.assertRaisesRegexp(exceptions.ValidationFailed,
                                     "Invalid JSON body in request"):
            request_fit_schema(base.fake_request_bad_invalid_json_body)

    def test_schema_base(self):
        with self.assertRaises(errors.InvalidResourceName):
            service.ServiceSchema.get_schema("invalid_resource", "PUT")
        with self.assertRaises(errors.InvalidOperation):
            service.ServiceSchema.get_schema("service", "INVALID_HTTP_VERB")

    def test_accept_header(self):
        req = base.DummyRequestWithInvalidHeader()
        resp = helpers.DummyResponse()

        with self.assertRaises(helpers.falcon.HTTPNotAcceptable):
            helpers.require_accepts_json_falcon(req, resp)

    def test_falcon_endpoint(self):
        class DummyResponse(object):
            pass

        response = DummyResponse()

        global error_count

        # Try to call with good inputs
        oldcount = base.error_count
        ret = self.ep.get_falcon_style(base.fake_request_good, response)
        self.assertEqual(oldcount, base.error_count)
        self.assertEqual(
            ret,
            "Hello, World!",
            "testing not passed on endpoint: get_falcon_style with valid data")

        # Try to call with bad inputs
        oldcount = base.error_count
        self.ep.get_falcon_style(
            base.fake_request_bad_missing_domain,
            response)
        self.assertEqual(oldcount + 1, base.error_count)

        # Try to call with bad inputs
        self.ep.get_falcon_style_custom_abort(
            base.fake_request_bad_missing_domain,
            response)
