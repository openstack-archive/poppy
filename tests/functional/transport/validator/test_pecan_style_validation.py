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

os.environ['PECAN_CONFIG'] = os.path.join(os.path.dirname(__file__),
                                          'config.py')
# For noese fix
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import test_service_validation


class PecanEndPointFunctionalTest(test_service_validation.BaseTestCase):

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
