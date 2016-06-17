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

import mock
from oslo_config import cfg
from oslo_log import log
import webtest

from poppy import bootstrap
from poppy.storage.mockdb import services
from tests.functional import base


class BaseFunctionalTest(base.TestCase):

    def setUp(self):
        super(BaseFunctionalTest, self).setUp()

        tests_path = os.path.abspath(os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)
                                ))))
        conf_path = os.path.join(tests_path, 'etc', 'default_functional.conf')
        cfg.CONF(args=[], default_config_files=[conf_path])
        self.b_obj = bootstrap.Bootstrap(cfg.CONF)

        # memoized_controllers module looks for log options being registered
        # register them here to avoid `cfg.ArgsAlreadyParsedError` when
        # running individual functional tests
        cfg.CONF.register_opts(log._options.logging_cli_opts)

        # mock the persistence part for taskflow distributed_task
        mock_persistence = mock.Mock()
        mock_persistence.__enter__ = mock.Mock()
        mock_persistence.__exit__ = mock.Mock()
        self.b_obj.distributed_task.persistence = mock.Mock()
        self.b_obj.distributed_task.persistence.return_value = mock_persistence
        self.b_obj.distributed_task.job_board = mock.Mock()
        self.b_obj.distributed_task.job_board.return_value = (
            mock_persistence.copy())
        self.b_obj.distributed_task.is_alive = mock.Mock(return_value=True)

        self.sps_api_client_mock = mock.MagicMock()
        if 'akamai' in self.b_obj.provider:
            # akamai driver was loaded. mock out queues
            akamai_driver = self.b_obj.provider['akamai'].obj

            mock_cert_info = mock.MagicMock()
            mock_cert_info.get_cert_config.return_value = {}

            mod_san_q = mock.MagicMock()
            mod_san_q.traverse_queue.return_value = []
            mod_san_q.mod_san_queue_backend.__len__.return_value = 0

            san_mapping_q = mock.MagicMock()
            san_mapping_q.traverse_queue.return_value = []

            akamai_driver.mod_san_queue = mod_san_q
            akamai_driver.san_mapping_queue = san_mapping_q
            akamai_driver.is_alive = mock.Mock(return_value=True)
            type(akamai_driver).cert_info_storage = mock_cert_info
            type(akamai_driver).sps_api_client = self.sps_api_client_mock

        # Note(tonytan4ever):Need this hack to preserve mockdb storage
        # controller's service cache
        # b_obj.manager.ssl_certificate_controller.storage_controller = (
        #     b_obj.manager.services_controller.storage_controller
        # )
        poppy_wsgi = self.b_obj.transport.app

        self.app = webtest.app.TestApp(poppy_wsgi)

    def tearDown(self):
        super(BaseFunctionalTest, self).tearDown()

        services.created_services = {}
        services.created_service_ids = []
        services.claimed_domains = []
        services.project_id_service_limit = {}
        services.service_count_per_project_id = {}

FunctionalTest = BaseFunctionalTest
