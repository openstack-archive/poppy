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
import json
import os
import re
import sys

import pecan
import pecan.testing
from webtest import app

from poppy.common import errors
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import service
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule
from tests.functional import base

# for pecan testing app
os.environ['PECAN_CONFIG'] = os.path.join(os.path.dirname(__file__),
                                          'config.py')
# For noese fix
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

error_count = 0


def abort(code):
    global error_count
    error_count = error_count + 1


@decorators.validation_function
def is_valid_json(r):
    """Ensures that input is a valid json string."""

    if len(r.body) == 0:
        return
    else:
        try:
            json.loads(r.body.decode('utf-8'))
        except Exception as e:
            e
            raise exceptions.ValidationFailed('Invalid JSON string')
        else:
            return


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


class DummyRequestWithInvalidHeader(DummyRequest):

    def client_accepts(self, header='application/json'):
        return False

    def accept(self, header='application/json'):
        return False


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
            basestring = unicode = str
            unicode  # For pep8: unicde is defined but not used.
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                                        (expected_regexp.pattern,
                                         str(exc_value)))
        return True


class BaseTestCase(base.TestCase):

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        """Assert a particular Exception has occurred.

        Fail unless an exception of class excClass is raised
           by callableObj when invoked with arguments args and keyword
           arguments kwargs. If a different type of exception is
           raised, it will not be caught, and the test case will be
           deemed to have suffered an error, exactly as for an
           unexpected exception.

           If called with callableObj omitted or None, will return a
           context object used like this::

                with self.assertRaises(SomeException):
                    do_something()

           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::

               with self.assertRaises(SomeException) as cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """

        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regexp."""
        context = _AssertRaisesContext(expected_exception, self,
                                       expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)

    def test_accept_header(self):
        req = DummyRequestWithInvalidHeader()
        resp = helpers.DummyResponse()
        try:
            with self.assertRaises(helpers.falcon.HTTPNotAcceptable):
                helpers.require_accepts_json_falcon(req, resp)
        except Exception as e:
            e
            pass

        with self.assertRaises(exceptions.ValidationFailed):
            helpers.req_accepts_json_pecan(req)


@decorators.validation_function
def is_response(candidate):
    pass


testing_schema = service.ServiceSchema.get_schema("service", "PUT")

request_fit_schema = functools.partial(
    helpers.with_schema_falcon,
    schema=testing_schema)


class DummyFalconEndpoint(object):
    # falcon style endpoint

    @decorators.validate(
        request=rule.Rule(request_fit_schema, lambda error_info: abort(404)),
        response=rule.Rule(is_response(), lambda error_info: abort(404))
    )
    def get_falcon_style(self, request, response):
        return "Hello, World!"

    @decorators.validate(
        request=rule.Rule(request_fit_schema,
                          helpers.custom_abort_falcon),
        response=rule.Rule(is_response(),
                           helpers.custom_abort_falcon)
    )
    def get_falcon_style_custom_abort(self, request, response):
        return "Hello, World!"


class DummyPecanEndpoint(object):

    @pecan.expose(generic=True)
    @helpers.with_schema_pecan(pecan.request, schema=testing_schema)
    def index(self):
        return "Hello, World!"

    @index.when(method='PUT')
    @decorators.validate(
        request=rule.Rule(is_valid_json(),
                          lambda error_info: pecan.abort(400),
                          stoplight_helpers.pecan_getter)
    )
    def index_put(self):
        return "Hello, World!"


def test_fake_falcon():
    helpers.falcon.HTTPNotAcceptable("nothing")


class TestFalconStyleValidationFunctions(BaseTestCase):

    def test_with_schema_falcon(self):
        self.assertEqual(
            helpers.with_schema_falcon(
                fake_request_good,
                schema=testing_schema),
            None)
        with self.assertRaisesRegexp(exceptions.ValidationFailed, "domain"):
            helpers.with_schema_falcon(
                fake_request_bad_missing_domain,
                schema=testing_schema)
        with self.assertRaisesRegexp(exceptions.ValidationFailed,
                                     "Invalid JSON body in request"):
            helpers.with_schema_falcon(
                fake_request_bad_invalid_json_body,
                schema=testing_schema)

    def test_partial_with_schema(self):
        self.assertEqual(request_fit_schema(fake_request_good), None)
        with self.assertRaisesRegexp(exceptions.ValidationFailed, "domain"):
            request_fit_schema(fake_request_bad_missing_domain)
        with self.assertRaisesRegexp(exceptions.ValidationFailed,
                                     "Invalid JSON body in request"):
            request_fit_schema(fake_request_bad_invalid_json_body)

    def test_schema_base(self):
        with self.assertRaises(errors.InvalidResourceName):
            service.ServiceSchema.get_schema("invalid_resource", "PUT")
        with self.assertRaises(errors.InvalidOperation):
            service.ServiceSchema.get_schema("service", "INVALID_HTTP_VERB")


class TestValidationDecoratorsFalcon(BaseTestCase):

    def setUp(self):
        self.ep = DummyFalconEndpoint()
        super(TestValidationDecoratorsFalcon, self).setUp()

    def test_falcon_endpoint(self):
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

        # Try to call with bad inputs
        self.ep.get_falcon_style_custom_abort(
            fake_request_bad_missing_domain,
            response)


class PecanEndPointFunctionalTest(BaseTestCase):

    """Sets up a Test Pecan endpoint."""

    def setUp(self):
        self.app = pecan.testing.load_test_app(
            os.path.join(os.path.dirname(__file__),
                         'config.py'
                         ))
        super(PecanEndPointFunctionalTest, self).setUp()

    def tearDown(self):
        pecan.set_config({}, overwrite=True)
        super(PecanEndPointFunctionalTest, self).tearDown()


class TestValidationDecoratorsPecan(PecanEndPointFunctionalTest):

    def test_pecan_endpoint_post(self):
        resp = self.app.post(
            '/',
            params=fake_request_good.body,
            headers={
                "Content-Type": "application/json;charset=utf-8"})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
        with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
            self.app.post('/', params=fake_request_bad_missing_domain.body,
                          headers={"Content-Type": "application/json"})
        with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
            self.app.post('/', params=fake_request_bad_invalid_json_body.body,
                          headers={"Content-Type": "application/json"})
