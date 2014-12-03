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
import re

from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions
from tests.functional import base


error_count = 0


def abort(code):
    global error_count
    error_count = error_count + 1


@decorators.validation_function
def is_valid_json(r):
    '''Test for a valid JSON string.'''
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
        self.method = 'POST'
        self.body = json.dumps({
            'name': 'fake_service_name',
            'domains': [
                {'domain': 'www.mywebsite.com'},
                {'domain': 'blog.mywebsite.com'},
            ],
            'origins': [
                {
                    'origin': 'mywebsite.com',
                    'port': 80,
                    'ssl': False
                },
                {
                    'origin': 'mywebsite.com',
                    'rules': [{
                        'name': 'img',
                        'request_url': '/img'
                    }]
                }
            ],
            'caching': [
                {'name': 'default', 'ttl': 3600},
                {'name': 'home',
                 'ttl': 17200,
                 'rules': [
                     {'name': 'index', 'request_url': '/index.htm'}
                 ]
                 },
                {"name": "images",
                 "ttl": 12800,
                 "rules": [
                     {"name": "img", "request_url": "/img/*"}
                 ]
                 }
            ],
            "flavor_id": "standard"
        })


class DummyRequestWithInvalidHeader(DummyRequest):

    def client_accepts(self, header='application/json'):
        return False

    def accept(self, header='application/json'):
        return False


fake_request_good = DummyRequest()
fake_request_bad_missing_domain = DummyRequest()
fake_request_bad_missing_domain.body = json.dumps({
    'name': 'fake_service_name',
    'origins': [
        {
            'origin': 'mywebsite.com',
            'port': 80,
            'ssl': False
        }
    ],
    'caching': [
        {'name': 'default', 'ttl': 3600},
        {'name': 'home',
         'ttl': 17200,
                 'rules': [
                     {'name': 'index', 'request_url': '/index.htm'}
                 ]
         },
        {'name': 'images',
                 'ttl': 12800,
                 'rules': [
                     {'name': 'images', 'request_url': '*.png'}
                 ]
         }
    ],
    "flavor_id": "standard"
})
fake_request_bad_invalid_json_body = DummyRequest()
fake_request_bad_invalid_json_body.body = '{'


class _AssertRaisesContext(object):

    '''A context manager used to implement TestCase.assertRaises* methods.'''

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
                '{0} not raised'.format(exc_name))
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
        '''Check the expected Exception is raised.

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
        '''
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        '''Asserts that the message in a raised exception matches a regexp.'''
        context = _AssertRaisesContext(expected_exception, self,
                                       expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)


@decorators.validation_function
def is_response(candidate):
    pass
