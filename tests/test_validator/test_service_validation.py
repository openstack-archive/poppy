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

from cdn.transport.validators.helpers import with_schema_falcon,\
    with_schema_pecan
from cdn.transport.validators.schemas import service

from cdn.transport.validators.stoplight import Rule, validate,\
    validation_function
from cdn.transport.validators.stoplight.exceptions import ValidationFailed

from pecan import expose, set_config, request
from webtest.app import AppError

import json
from unittest import TestCase

import functools
import os
import re

# for pecan testing app
os.environ['PECAN_CONFIG'] = os.path.join(os.path.dirname(__file__),
                                          'config.py')
from pecan.testing import load_test_app


error_count = 0


def abort(code):
    global error_count
    error_count = error_count + 1


class DummyRequest(object):

    def __init__(self):
        self.headers = dict(header1='headervalue1')
        self.method = "PUT"
        self.body = json.dumps({
            "domains": [
                {"domain": "www.mywebsite.com"},
                {"domain": "blog.mywebsite.com"},
            ],
            "origins": [
                {
                    "origin": "mywebsite.com",
                    "port": 80,
                    "ssl": False
                },
                {
                    "origin": "mywebsite.com",
                }
            ],
            "caching": [
                {"name": "default", "ttl": 3600},
                {"name": "home",
                 "ttl": 17200,
                 "rules": [
                     {"name": "index", "request_url": "/index.htm"}
                 ]
                 },
                {"name": "images",
                 "ttl": 12800,
                 }
            ]
        })


fake_request_good = DummyRequest()
fake_request_bad_missing_domain = DummyRequest()
fake_request_bad_missing_domain.body = json.dumps({
    "origins": [
        {
            "origin": "mywebsite.com",
            "port": 80,
            "ssl": False
        }
    ],
    "caching": [
        {"name": "default", "ttl": 3600},
        {"name": "home",
         "ttl": 17200,
                 "rules": [
                     {"name": "index", "request_url": "/index.htm"}
                 ]
         },
        {"name": "images",
                 "ttl": 12800,
                 "rules": [
                     {"name": "images", "request_url": "*.png"}
                 ]
         }
    ]
})
fake_request_bad_invalid_json_body = DummyRequest()
fake_request_bad_invalid_json_body.body = "{"


class _AssertRaisesContext(object):
    """A context manager used to implement TestCase.assertRaises* methods."""

    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            return False  # let unexpected exceptions pass through
        self.exception = exc_value  # store for later retrieval
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        try:
            basestring
        except NameError:
            # Python 3 compatibility
            basestring = unicode
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                                        (expected_regexp.pattern,
                                         str(exc_value)))
        return True


class BaseTestCase(TestCase):
    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regexp."""
        context = _AssertRaisesContext(expected_exception, self,
                                       expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)


@validation_function
def is_response(candidate):
    pass


testing_schema = service.ServiceSchema.get_schema("service", "PUT")

request_fit_schema = functools.partial(
    with_schema_falcon,
    schema=testing_schema)


class DummyFalconEndpoint(object):
    # falcon style endpoint

    @validate(
        request=Rule(request_fit_schema, lambda: abort(404)),
        response=Rule(is_response(), lambda: abort(404))
    )
    def get_falcon_style(self, request, response):
        return "Hello, World!"


class DummyPecanEndpoint(object):

    @expose()
    @with_schema_pecan(request, schema=testing_schema)
    def index(self):
        return "Hello, World!"


class TestFalconStyleValidationFunctions(BaseTestCase):

    def test_with_schema_falcon(self):
        self.assertEquals(
            with_schema_falcon(
                fake_request_good,
                schema=testing_schema),
            None)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            with_schema_falcon(
                fake_request_bad_missing_domain,
                schema=testing_schema)
        with self.assertRaisesRegexp(ValidationFailed,
                                     "Invalid JSON body in request"):
            with_schema_falcon(
                fake_request_bad_invalid_json_body,
                schema=testing_schema)

    def test_partial_with_schema(self):
        self.assertEquals(request_fit_schema(fake_request_good), None)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            request_fit_schema(fake_request_bad_missing_domain)
        with self.assertRaisesRegexp(ValidationFailed,
                                     "Invalid JSON body in request"):
            request_fit_schema(fake_request_bad_invalid_json_body)


class TestValidationDecoratorsFalcon(BaseTestCase):

    def setUp(self):
        self.ep = DummyFalconEndpoint()

    def test_falcon_eps(self):
        class DummyResponse(object):
            pass

        response = DummyResponse()

        global error_count

        # Try to call with good inputs
        oldcount = error_count
        ret = self.ep.get_falcon_style(fake_request_good, response)
        self.assertEqual(oldcount, error_count)
        self.assertEqual(
            ret,
            "Hello, World!",
            "testing not passed on endpoint: get_falcon_style with valid data")

        # Try to call with bad inputs
        oldcount = error_count
        self.ep.get_falcon_style(
            fake_request_bad_missing_domain,
            response)
        self.assertEqual(oldcount + 1, error_count)


class PecanEndPointFunctionalTest(BaseTestCase):

    """A Simple PecanFunctionalTest base class that sets up a
    Pecan endpoint (endpoint class: DummyPecanEndpoint)
    """

    def setUp(self):
        self.app = load_test_app(os.path.join(os.path.dirname(__file__),
                                              'config.py'
                                              ))

    def tearDown(self):
        set_config({}, overwrite=True)


class TestValidationDecoratorsPecan(PecanEndPointFunctionalTest):

    def test_pecan_endpoint_put(self):
        # print(fake_request_good.body)
        resp = self.app.put(
            '/',
            params=fake_request_good.body,
            headers={
                "Content-Type": "application/json;charset=utf-8"})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
        with self.assertRaisesRegexp(AppError, "400 Bad Request"):
            self.app.put('/', params=fake_request_bad_missing_domain.body,
                         headers={"Content-Type": "application/json"})
        #assert resp.status_int == 400
