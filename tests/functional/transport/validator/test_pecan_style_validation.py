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

import os
import sys

import pecan
from pecan.testing import load_test_app
from webtest import app

from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import service
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule
import test_falcon_style_validation

# For noese path fix
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

os.environ['PECAN_CONFIG'] = os.path.join(os.path.dirname(__file__),
                                          'config.py')

testing_schema = service.ServiceSchema.get_schema("service", "PUT")


@decorators.validation_function
def is_valid_json(r):
    """Simple validation function for testing purposes
    that ensures that input is a valid json string
    """
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
    
    @index.when(method='DELETE')
    @helpers.with_schema_pecan(pecan.request, schema=testing_schema)
    def index_delete(self):
        return "Hello, World!"
    
    @index.when(method='PATCH')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_schema(
                None),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def index_patch(self):
        return "Hello, World!"


class PecanEndPointFunctionalTest(test_falcon_style_validation.BaseTestCase):

    """A Simple PecanFunctionalTest base class that sets up a
    Pecan endpoint (endpoint class: DummyPecanEndpoint)
    """

    def setUp(self):
        self.app = load_test_app(os.path.join(os.path.dirname(__file__),
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
            params=test_falcon_style_validation.fake_request_good.body,
            headers={
                "Content-Type": "application/json;charset=utf-8"})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
        with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
            self.app.post('/', params=test_falcon_style_validation.\
                                    fake_request_bad_missing_domain.body,
                          headers={"Content-Type": "application/json"})
        with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
            self.app.post('/', params=test_falcon_style_validation.\
                                    fake_request_bad_invalid_json_body.body,
                          headers={"Content-Type": "application/json"})
    
    def test_pecan_endpoint_delete(self):
        resp = self.app.delete('/')
        self.assertEqual(resp.status_int, 200)
    
    def test_pecan_endpoint_patch(self):
        resp = self.app.patch('/',
                    params=test_falcon_style_validation.fake_request_good.body,
                    headers={"Content-Type": "application/json;charset=utf-8"})
        self.assertEqual(resp.status_int, 200)
    
    def test_pecan_endpoint_put(self):
        resp = self.app.put(
            '/',
            headers={
                "Content-Type": "application/json;charset=utf-8"})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
        with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
            self.app.put('/', params='{',
                         headers={"Content-Type":
                                  "application/json;charset=utf-8"})
