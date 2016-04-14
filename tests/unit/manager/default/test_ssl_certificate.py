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
import mock
from oslo_config import cfg
import testtools

from poppy.manager.default import driver
from poppy.manager.default import ssl_certificate
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

        provider_mocks = {
            'akamai': mock.Mock(provider_name="Akamai"),
            'maxcdn': mock.Mock(provider_name='MaxCDN'),
            'cloudfront': mock.Mock(provider_name='CloudFront'),
            'fastly': mock.Mock(provider_name='Fastly'),
            'mock': mock.Mock(provider_name='Mock')
        }

        # mock a stevedore provider extension
        def get_provider_by_name(name):
            obj_mock = provider_mocks[name]
            obj_mock.san_cert_cnames = ["san1", "san2"]
            obj_mock.akamai_sps_api_base_url = 'akamai_base_url/{spsId}'

            provider = mock.Mock(obj=obj_mock)
            return provider

        def provider_membership(key):
            return True if key in provider_mocks else False

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

    def test_update_san_cert_configuration_positive(self):
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
