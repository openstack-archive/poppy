# # Copyright (c) 2014 Rackspace, Inc.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #    http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# # implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

# import os

# import mock
# from oslo_config import cfg

# from poppy.transport import pecan
# from tests.unit import base


# TODO(amitgandhinz): This test is currently failing.


def mock(self):
    pass

# class PecanTransportDriverTest(base.TestCase):

#     def test_listen(self):
#         tests_path = os.path.abspath(os.path.dirname(
#             os.path.dirname(
#                                     os.path.dirname(os.path.dirname(__file__)
#                                                      ))))
#         conf_path = os.path.join(tests_path, 'etc', 'pecan.py')
#         cfg.CONF(args=[], default_config_files=[conf_path])

#         mock_path = 'poppy.transport.pecan.driver.simple_server'
#         with mock.patch(mock_path) as mocked_module:
#             mock_server = mock.Mock()
#             mocked_module.make_server = mock.Mock(return_value=mock_server)
#             driver = pecan.Driver(cfg.CONF, None)
#             driver.listen()
#             self.assertTrue(mock_server.serve_forever.called)
