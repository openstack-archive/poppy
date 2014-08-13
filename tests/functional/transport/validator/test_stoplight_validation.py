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

from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions
from poppy.transport.validators.stoplight import rule
from tests.functional.transport.validator import base


@decorators.validation_function
def is_upper(z):
    """Ensures Uppercase."""
    if z.upper() != z:
        raise exceptions.ValidationFailed('{0} no uppercase'.format(z))


other_vals = dict()
get_other_val = other_vals.get


class DummyRequest(object):

    def __init__(self):
        self.headers = dict(header1='headervalue1')


class DummyResponse(object):
    pass


@decorators.validation_function
def is_request(candidate):
    if not isinstance(candidate, DummyRequest):
        raise exceptions.ValidationFailed('Input must be a request')


@decorators.validation_function
def is_response(candidate):
    if not isinstance(candidate, DummyResponse):
        raise exceptions.ValidationFailed('Input must be a response')


RequestRule = rule.Rule(is_request(), lambda error_info: base.abort(404))
ResponseRule = rule.Rule(is_response(), lambda error_info: base.abort(404))
UppercaseRule = rule.Rule(is_upper(), lambda error_info: base.abort(404))


class DummyEndpoint(object):

    # This should throw a ValidationProgrammingError
    # when called because the user did not actually
    # call validate_upper.

    # Note: the lambda in this function can never actually be
    # called, so we use no cover here

    @decorators.validate(
        value=rule.Rule(
            is_upper,
            lambda error_info: base.abort(404)))  # pragma: no cover
    def get_value_programming_error(self, value):
        # This function body should never be
        # callable since the validation error
        # should not allow it to be called
        assert False  # pragma: no cover

    @decorators.validate(
        value1=rule.Rule(is_upper(), lambda error_info: base.abort(404)),
        value2=rule.Rule(is_upper(), lambda error_info: base.abort(404)),
        value3=rule.Rule(is_upper(), lambda error_info: base.abort(404))
    )  # pragma: no cover
    def get_value_happy_path(self, value1, value2, value3):
        return value1 + value2 + value3

    @decorators.validate(
        value1=rule.Rule(is_upper(), lambda: base.abort(404)),
        value2=rule.Rule(is_upper(empty_ok=True),
                         lambda error_info: base.abort(404),
                         get_other_val),
    )  # pragma: no cover
    def get_value_with_getter(self, value1):
        global other_vals
        return value1 + other_vals.get('value2')

    # Falcon-style endpoint
    @decorators.validate(
        request=rule.Rule(is_request(), lambda error_info: base.abort(404)),
        response=rule.Rule(is_response(), lambda error_info: base.abort(404)),
        value=rule.Rule(is_upper(), lambda error_info: base.abort(404))
    )
    def get_falcon_style(self, request, response, value):
        return value

    # Falcon-style w/ declared rules
    @decorators.validate(request=RequestRule, response=ResponseRule,
                         value=UppercaseRule)
    def get_falcon_with_declared_rules(self, request, response, value):
        return value


class TestValidationFunction(base.BaseTestCase):

    def test_empty_ok(self):
        is_upper(empty_ok=True)('')

        with self.assertRaises(exceptions.ValidationFailed):
            is_upper()('')

        is_upper(none_ok=True)(None)

        with self.assertRaises(exceptions.ValidationFailed):
            is_upper()(None)


class TestValidationDecorator(base.BaseTestCase):

    def setUp(self):
        self.ep = DummyEndpoint()
        super(TestValidationDecorator, self).setUp()

    def test_programming_error(self):
        with self.assertRaises(exceptions.ValidationProgrammingError):
            self.ep.get_value_programming_error('AT_ME')

    def test_falcon_style(self):

        global error_count

        request = DummyRequest()
        response = DummyResponse()

        # Try to call with missing params. The validation
        # function should never get called
        oldcount = base.error_count
        self.ep.get_falcon_style(response, 'HELLO')
        self.assertEqual(oldcount + 1, base.error_count)

        # Try to pass a string to a positional argument
        # where a response is expected
        oldcount = base.error_count
        self.ep.get_falcon_style(request, "bogusinput", 'HELLO')
        self.assertEqual(oldcount + 1, base.error_count)

        # Pass in as kwvalues with good input but out of
        # typical order (should succeed)
        oldcount = base.error_count
        self.ep.get_falcon_style(response=response, value='HELLO',
                                 request=request)
        self.assertEqual(oldcount, base.error_count)

        # Pass in as kwvalues with good input but out of
        # typical order with an invalid value (lower-case 'h')
        oldcount = base.error_count
        self.ep.get_falcon_style(response=response, value='hELLO',
                                 request=request)
        self.assertEqual(oldcount + 1, base.error_count)

        # Pass in as kwvalues with good input but out of typical order
        # and pass an invalid value. Note that here the response is
        # assigned to request, etc.
        oldcount = base.error_count
        self.ep.get_falcon_style(response=request, value='HELLO',
                                 request=response)
        self.assertEqual(oldcount + 1, base.error_count)

        # Happy path
        oldcount = base.error_count
        self.ep.get_falcon_style(request, response, 'HELLO')
        self.assertEqual(oldcount, base.error_count)

    def test_falcon_style_declared_rules(self):
        # The following tests repeat the above
        # tests, but this time they test using the
        # endpoint with the rules being declared
        # separately. See get_falcon_with_declared_rules above

        request = DummyRequest()
        response = DummyResponse()

        # Try to call with missing params. The validation
        # function should never get called
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(response, 'HELLO')
        self.assertEqual(oldcount + 1, base.error_count)

        # Try to pass a string to a positional argument
        # where a response is expected
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(request, "bogusinput", 'HELLO')
        self.assertEqual(oldcount + 1, base.error_count)

        # Pass in as kwvalues with good input but out of
        # typical order (should succeed)
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(
            response=response,
            value='HELLO',
            request=request)
        self.assertEqual(oldcount, base.error_count)

        # Pass in as kwvalues with good input but out of
        # typical order with an invalid value (lower-case 'h')
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(
            response=response,
            value='hELLO',
            request=request)
        self.assertEqual(oldcount + 1, base.error_count)

        # Pass in as kwvalues with good input but out of typical order
        # and pass an invalid value. Note that here the response is
        # assigned to request, etc.
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(response=request, value='HELLO',
                                               request=response)
        self.assertEqual(oldcount + 1, base.error_count)

        # Happy path
        oldcount = base.error_count
        self.ep.get_falcon_with_declared_rules(request, response, 'HELLO')
        self.assertEqual(oldcount, base.error_count)

    def test_validation_passed(self):
        # Should not throw
        res = self.ep.get_value_happy_path('WHATEVER', 'HELLO', 'YES')
        self.assertEqual('WHATEVERHELLOYES', res)

    def test_validation_failed(self):
        # Validation should have failed, and
        # we should have seen a tick in the error count
        oldcount = base.error_count
        self.ep.get_value_happy_path('WHAtEVER', 'HELLO', 'YES')
        self.assertEqual(oldcount + 1, base.error_count)

    def test_validating_none_value(self):
        # Check passing a None value. This decorator does
        # not permit none values.
        oldcount = base.error_count
        self.ep.get_value_happy_path(None, 'HELLO', 'YES')
        self.assertEqual(oldcount + 1, base.error_count)

    def test_getter(self):
        global other_vals

        other_vals['value2'] = 'HELLO'

        # Now have our validation actually try to
        # get those values

        # This should succeed
        res = self.ep.get_value_with_getter('TEST')
        self.assertEqual('TESTHELLO', res)

        # check empty_ok
        other_vals['value2'] = ''
        res = self.ep.get_value_with_getter('TEST')
        self.assertEqual('TEST', res)
