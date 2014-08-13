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

# import os

# import pecan
# import pecan.testing
# from webtest import app

# from poppy.transport.validators import helpers
# from poppy.transport.validators.stoplight import exceptions
# from tests.functional.transport.validator import base

# TODO(amitgandhinz): This whole file needs refactoring.
# TODO(amitgandhinz): The pecan and falcon validation should live in the
#                     transport/pecan and transport/falcon folders
# TODO(amitgandhinz): The transport/validator modules should test just the
#                     validator logic, independant of the transport used.


def mock(self):
    pass

# class PecanEndPointFunctionalBase(base.BaseTestCase):

#     """Sets up a Test Pecan endpoint."""

#     def setUp(self):

#         tests_path = os.path.abspath(os.path.dirname(
#             os.path.dirname(
#                 os.path.dirname(os.path.dirname(__file__)
#                                 ))))

#         self.app = pecan.testing.load_test_app(
#             os.path.join(tests_path, 'etc', 'pecan.py')
#         )

#         super(PecanEndPointFunctionalBase, self).setUp()

#     def tearDown(self):
#         pecan.set_config({}, overwrite=True)
#         super(PecanEndPointFunctionalBase, self).tearDown()


# class TestValidationFunctionsPecan(PecanEndPointFunctionalBase):

#     def test_pecan_endpoint_post(self):
#         resp = self.app.post(
#             '/',
#             params=base.fake_request_good.body,
#             headers={
#                 "Content-Type": "application/json;charset=utf-8"})
#         self.assertEqual(resp.status_int, 200)
#         self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
#         with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
#             self.app.post('/',
#                           params=base.fake_request_bad_missing_domain.body,
#                           headers={"Content-Type": "application/json"})
#         with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
#             self.app.post('/',
#                          params=base.fake_request_bad_invalid_json_body.body,
#                           headers={"Content-Type": "application/json"})

#     def test_accept_header(self):
#         req = base.DummyRequestWithInvalidHeader()

#         with self.assertRaises(exceptions.ValidationFailed):
#             helpers.req_accepts_json_pecan(req)

#     def test_pecan_endpoint_put(self):
#         resp = self.app.put(
#             '/',
#             headers={
#                 "Content-Type": "application/json;charset=utf-8"})
#         self.assertEqual(resp.status_int, 200)
#         self.assertEqual(resp.body.decode('utf-8'), "Hello, World!")
#         with self.assertRaisesRegexp(app.AppError, "400 Bad Request"):
#             self.app.put('/', params='{',
#                          headers={"Content-Type":
#                                   "application/json;charset=utf-8"})
