# Copyright (c) 2016 Rackspace, Inc.
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

import ddt
import json
import mock
from oslo_config import cfg
import testtools

from poppy.manager.default import driver
from poppy.manager.default import ssl_certificate
from poppy.model import ssl_certificate as ssl_cert_model
from tests.unit import base


@ddt.ddt
class DefaultSSLCertificateControllerTests(base.TestCase):

    @mock.patch('poppy.bootstrap.Bootstrap')
    @mock.patch('poppy.notification.base.driver.NotificationDriverBase')
    @mock.patch('poppy.dns.base.driver.DNSDriverBase')
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.distributed_task.base.driver.DistributedTaskDriverBase')
    @mock.patch('poppy.metrics.base.driver.MetricsDriverBase')
    def setUp(self, mock_metrics, mock_distributed_task, mock_storage,
              mock_dns, mock_notification, mock_bootstrap):

        super(DefaultSSLCertificateControllerTests, self).setUp()

        conf = cfg.ConfigOpts()

        self.provider_mocks = {
            'akamai': mock.Mock(provider_name="Akamai"),
            'maxcdn': mock.Mock(provider_name='MaxCDN'),
            'cloudfront': mock.Mock(provider_name='CloudFront'),
            'fastly': mock.Mock(provider_name='Fastly'),
            'mock': mock.Mock(provider_name='Mock')
        }

        # mock a stevedore provider extension
        def get_provider_by_name(name):
            obj_mock = self.provider_mocks[name]
            obj_mock.san_cert_cnames = ["san1", "san2"]
            obj_mock.akamai_sps_api_base_url = 'akamai_base_url/{spsId}'

            provider = mock.Mock(obj=obj_mock)
            return provider

        def provider_membership(key):
            return True if key in self.provider_mocks else False

        self.mock_providers = mock.MagicMock()
        self.mock_providers.__getitem__.side_effect = get_provider_by_name
        self.mock_providers.__contains__.side_effect = provider_membership
        self.manager_driver = driver.DefaultManagerDriver(
            conf,
            mock_storage,
            self.mock_providers,
            mock_dns,
            mock_distributed_task,
            mock_notification,
            mock_metrics
        )
        self.scc = ssl_certificate.DefaultSSLCertificateController(
            self.manager_driver
        )

    def test_create_ssl_certificate_exception_validation(self):
        cert_obj = ssl_cert_model.SSLCertificate(
            'flavor_id',
            'invalid_domain',
            'san',
            project_id='project_id'
        )

        with testtools.ExpectedException(ValueError):
            self.scc.create_ssl_certificate('project_id', cert_obj=cert_obj)

    def test_create_ssl_certificate_exception_storage_create_cert(self):
        cert_obj = ssl_cert_model.SSLCertificate(
            'flavor_id',
            'www.valid-domain.com',
            'san',
            project_id='project_id'
        )

        self.scc.storage.create_certificate.side_effect = ValueError(
            'Mock -- Cert already exists!')
        with testtools.ExpectedException(ValueError):
            self.scc.create_ssl_certificate('project_id', cert_obj=cert_obj)

    def test_get_san_cert_configuration_positive(self):
        resp = self.scc.get_san_cert_configuration("san1")
        self.assertIsNotNone(resp)

    def test_get_san_cert_configuration_positive_no_akamai_provider(self):
        del self.provider_mocks['akamai']
        resp = self.scc.get_san_cert_configuration("san1")
        self.assertEqual({}, resp)

    def test_get_san_cert_configuration_invalid_san_cert_cname(self):
        with testtools.ExpectedException(ValueError):
            self.scc.get_san_cert_configuration("non-existant")

    def test_set_san_cert_hostname_limit_positive(self):
        resp = mock.Mock()
        resp.status_code = 200
        resp.json.return_value = {
            'requestList': [
                {
                    'jobId': '5555'
                }
            ]
        }
        api_client = self.mock_providers['akamai'].obj.sps_api_client
        api_client.get.return_value = resp

        self.scc.update_san_cert_configuration("san1", {"spsId": '1234'})

        self.assertTrue(api_client.get.called)
        api_client.get.assert_called_once_with(
            self.mock_providers['akamai'].obj.akamai_sps_api_base_url.format(
                spsId=1234
            )
        )

    def test_update_san_cert_configuration_positive(self):

        self.scc.set_san_cert_hostname_limit(
            {"san_cert_hostname_limit": '1234'}
        )

        cert_info_storage = self.mock_providers['akamai'].obj.cert_info_storage

        cert_info_storage.set_san_cert_hostname_limit.\
            assert_called_once_with('1234')

    def test_update_san_cert_configuration_negative(self):

        with testtools.ExpectedException(ValueError):
            self.scc.set_san_cert_hostname_limit(
                {"invalid_setting_name": '1234'}
            )

        cert_info_storage = self.mock_providers['akamai'].obj.cert_info_storage

        self.assertFalse(
            cert_info_storage.set_san_cert_hostname_limit.called)

    def test_update_san_cert_configuration_no_sps_id(self):
        api_client = self.mock_providers['akamai'].obj.sps_api_client

        self.scc.update_san_cert_configuration("san1", {"spsId": None})

        self.assertEqual(False, api_client.called)

    def test_update_san_cert_invalid_san_cert_cname(self):

        with testtools.ExpectedException(ValueError):
            self.scc.update_san_cert_configuration("non-existant",
                                                   {"spsId": '1234'})

    def test_update_san_cert_configuration_api_failure(self):
        resp = mock.Mock()
        resp.status_code = 404
        resp.text = 'spsId Not Found'
        api_client = self.mock_providers['akamai'].obj.sps_api_client
        api_client.get.return_value = resp

        err_text = "SPS GET Request failed. Exception: spsId Not Found"
        with testtools.ExpectedException(RuntimeError, value_re=err_text):
            self.scc.update_san_cert_configuration("san1", {"spsId": '1234'})

        self.assertTrue(api_client.get.called)
        api_client.get.assert_called_once_with(
            self.mock_providers['akamai'].obj.akamai_sps_api_base_url.format(
                spsId=1234
            )
        )

    def test_get_san_retry_list(self):
        self.manager_driver.providers[
            'akamai'].obj.mod_san_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            })
        ]

        self.assertEqual(1, len(self.scc.get_san_retry_list()))

    def test_update_san_retry_list(self):
        original_queue_data = [{
            "domain_name": "a_domain",
            "project_id": "00000",
            "flavor_id": "flavor",
            "validate_service": True
        }]

        akamai_driver = self.manager_driver.providers[
            'akamai'].obj
        akamai_driver.mod_san_queue.traverse_queue.return_value = [
            json.dumps(original_queue_data)
        ]
        akamai_driver.mod_san_queue.put_queue_data.side_effect = lambda \
            value: value

        new_queue_data = [
            {
                "domain_name": "b_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }
        ]

        cert_domain_mock = mock.Mock()
        cert_domain_mock.get_cert_status.return_value = "create_in_progress"
        self.scc.storage.get_certs_by_domain. \
            return_value = cert_domain_mock

        res, deleted = self.scc.update_san_retry_list(new_queue_data)

        self.assertEqual(new_queue_data, res)

        self.assertEqual(
            True,
            self.scc.storage.get_certs_by_domain.called
        )
        self.assertEqual(
            True,
            akamai_driver.mod_san_queue.traverse_queue.called
        )
        self.assertEqual(
            True,
            akamai_driver.mod_san_queue.put_queue_data.called
        )

    def test_update_san_retry_list_cert_deployed_error(self):
        queue_data = [
            {
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }
        ]

        cert_domain_mock = mock.Mock()
        cert_domain_mock.get_cert_status.return_value = "deployed"
        self.scc.storage.get_certs_by_domain. \
            return_value = cert_domain_mock

        with testtools.ExpectedException(ValueError):
            self.scc.update_san_retry_list(queue_data)

        self.assertEqual(
            True,
            self.scc.storage.get_certs_by_domain.called
        )

    def test_rerun_san_retry_list(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps({
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }), encoding='utf-8')
        ]
        self.scc.storage.get_certs_by_domain. \
            return_value = []

        self.scc.rerun_san_retry_list()

        self.assertEqual(
            True,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_rerun_san_retry_list_exception_service_validation(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        test_queue_item = {
            "domain_name": "a_domain",
            "project_id": "00000",
            "flavor_id": "flavor",
            "validate_service": True
        }
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps(test_queue_item), encoding='utf-8')
        ]

        self.scc.service_storage.get_service_details_by_domain_name. \
            return_value = None

        with mock.patch('oslo_log.log.KeywordArgumentAdapter.error') as logger:
            self.scc.rerun_san_retry_list()

            self.assertTrue(logger.called)
            args, _ = logger.call_args
            self.assertTrue(test_queue_item["domain_name"] in args[0])
            self.assertTrue(test_queue_item["project_id"] in args[0])
            self.assertTrue(test_queue_item["flavor_id"] in args[0])
            self.assertTrue(
                str(test_queue_item["validate_service"]) in args[0]
            )

        self.assertEqual(
            False,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_rerun_san_retry_list_exception_cert_already_deployed(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        test_domain = "a_domain"
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps({
                "domain_name": test_domain,
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }), encoding='utf-8')
        ]

        cert_domain_mock = mock.Mock()
        cert_domain_mock.get_cert_status.return_value = "deployed"
        self.scc.storage.get_certs_by_domain. \
            return_value = cert_domain_mock

        with mock.patch('oslo_log.log.KeywordArgumentAdapter.error') as logger:
            self.scc.rerun_san_retry_list()

            self.assertTrue(logger.called)
            args, _ = logger.call_args
            self.assertEqual(
                (u'Certificate on {0} has already been provisioned '
                 'successfully.'.format(test_domain), ),
                args
            )

        self.assertEqual(
            False,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_rerun_san_retry_list_exception_flavor_get(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps({
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }), encoding='utf-8')
        ]

        self.scc.flavor_controller.get.side_effect = LookupError(
            "Mock -- Flavor not found!")

        self.scc.rerun_san_retry_list()

        self.assertEqual(True, mod_san_queue.enqueue_mod_san_request.called)
        self.assertEqual(
            False,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_rerun_san_retry_list_cert_deployed_second_check(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps({
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }), encoding='utf-8')
        ]

        cert_domain_mock = mock.Mock()
        cert_domain_mock.get_cert_status.return_value = "create_in_progress"
        cert_domain_mock_2 = mock.Mock()
        cert_domain_mock_2.get_cert_status.return_value = "deployed"
        self.scc.storage.get_certs_by_domain. \
            side_effect = [cert_domain_mock, cert_domain_mock_2]

        self.scc.rerun_san_retry_list()

        self.assertEqual(
            False,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_rerun_san_retry_list_cert_create_in_progress_second_check(self):
        mod_san_queue = self.manager_driver.providers[
            'akamai'].obj.mod_san_queue
        mod_san_queue.mod_san_queue_backend = mock.MagicMock()
        mod_san_queue.mod_san_queue_backend.__len__.side_effect = [1, 0]
        mod_san_queue.dequeue_mod_san_request.side_effect = [
            bytearray(json.dumps({
                "domain_name": "a_domain",
                "project_id": "00000",
                "flavor_id": "flavor",
                "validate_service": True
            }), encoding='utf-8')
        ]

        cert_domain_mock = mock.Mock()
        cert_domain_mock.get_cert_status.return_value = "create_in_progress"
        cert_domain_mock_2 = mock.Mock()
        cert_domain_mock_2.get_cert_status.return_value = "create_in_progress"
        self.scc.storage.get_certs_by_domain. \
            side_effect = [cert_domain_mock, cert_domain_mock_2]

        self.scc.rerun_san_retry_list()

        self.assertEqual(
            True,
            self.scc.distributed_task_controller.submit_task.called
        )

    def test_get_certs_by_status(self):
        result_list_mock = [mock.Mock()]
        self.scc.storage.get_certs_by_status.return_value = result_list_mock

        results = self.scc.get_certs_by_status("create_in_progress")

        self.assertEqual(result_list_mock, results)
