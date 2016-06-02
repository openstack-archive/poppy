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

import uuid

import ddt
import mock
from oslo_config import cfg

from poppy.common import errors
from poppy.manager.default import driver
from poppy.manager.default import services
from tests.unit import base


class StorageResult(object):

    def __init__(self, provider_details=None, flavor_id=None):
        self.provider_details = provider_details
        self.service_id = str(uuid.uuid4())
        self.flavor_id = flavor_id


@ddt.ddt
class DefaultManagerServiceTests(base.TestCase):

    @mock.patch('poppy.notification.base.driver.NotificationDriverBase')
    @mock.patch('poppy.dns.base.driver.DNSDriverBase')
    @mock.patch('poppy.storage.base.driver.StorageDriverBase')
    @mock.patch('poppy.distributed_task.base.driver.DistributedTaskDriverBase')
    @mock.patch('poppy.metrics.base.driver.MetricsDriverBase')
    def setUp(self, mock_metrics, mock_distributed_task,
              mock_storage, mock_dns, mock_notification):
        # NOTE(TheSriram): the mock.patch decorator applies mocks
        # in the reverse order of the arguments present
        super(DefaultManagerServiceTests, self).setUp()

        # create mocked config and driver
        conf = cfg.ConfigOpts()

        _DRIVER_DNS_OPTIONS = [
            cfg.IntOpt(
                'retries',
                default=5,
                help='Total number of Retries after '
                     'Exponentially Backing Off'),
            cfg.IntOpt(
                'min_backoff_range',
                default=20,
                help='Minimum Number of seconds to sleep between retries'),
            cfg.IntOpt(
                'max_backoff_range',
                default=30,
                help='Maximum Number of seconds to sleep between retries'),
        ]

        _PROVIDER_OPTIONS = [
            cfg.IntOpt(
                'default_cache_ttl',
                default=86400,
                help='Default ttl to be set, when no caching '
                     'rules are specified'),
        ]
        _MAX_SERVICE_OPTIONS = [
            cfg.IntOpt('max_services_per_project', default=20,
                       help='Default max service per project_id')
        ]
        _DRIVER_DNS_GROUP = 'driver:dns'
        _PROVIDER_GROUP = 'drivers:provider'
        _MAX_SERVICE_GROUP = 'drivers:storage'

        conf.register_opts(_PROVIDER_OPTIONS, group=_PROVIDER_GROUP)
        conf.register_opts(_DRIVER_DNS_OPTIONS, group=_DRIVER_DNS_GROUP)
        conf.register_opts(_MAX_SERVICE_OPTIONS, group=_MAX_SERVICE_GROUP)
        self.max_services_per_project = \
            conf[_MAX_SERVICE_GROUP].max_services_per_project

        provider_mock = mock.Mock()
        provider_mock.obj = mock.Mock()
        provider_mock.obj.service_controller = mock.Mock()
        provider_mock.obj.service_controller.get_metrics_by_domain = \
            mock.Mock(return_value=dict())

        # mock a stevedore provider extension
        def get_provider_by_name(name):
            name_p_name_mapping = {
                'mock_provider': provider_mock,
                'maxcdn': 'MaxCDN',
                'cloudfront': 'CloudFront',
                'fastly': 'Fastly',
                'mock': 'Mock',
                'Provider': 'Provider'
            }
            if name == 'mock_provider':
                return name_p_name_mapping[name]
            else:
                return mock.Mock(obj=mock.Mock(provider_name=(
                    name_p_name_mapping[name])))

        mock_providers = mock.MagicMock()
        mock_providers.__getitem__.side_effect = get_provider_by_name

        manager_driver = driver.DefaultManagerDriver(conf,
                                                     mock_storage,
                                                     mock_providers,
                                                     mock_dns,
                                                     mock_distributed_task,
                                                     mock_notification,
                                                     mock_metrics)

        # stubbed driver

        self.sc = services.DefaultServicesController(manager_driver)
        self.manager = manager_driver
        self.project_id = str(uuid.uuid4())
        self.domain_name = str(uuid.uuid4())

    def test_analytics_get_metrics_by_domain_provider_details_None(self):
        analytics_controller = \
            self.manager.analytics_controller
        extras = {}
        storage_controller = \
            self.manager.analytics_controller._driver.storage

        services_controller = storage_controller.services_controller
        services_controller.get_service_details_by_domain_name = \
            mock.Mock(return_value=StorageResult())
        self.assertRaises(errors.ServiceProviderDetailsNotFound,
                          analytics_controller.get_metrics_by_domain,
                          self.project_id, self.domain_name, **extras)

    def test_analytics_get_metrics_by_domain_service_not_found(self):
        analytics_controller = \
            self.manager.analytics_controller
        extras = {}
        storage_controller = \
            self.manager.analytics_controller._driver.storage

        services_controller = storage_controller.services_controller
        services_controller.get_service_details_by_domain_name = \
            mock.Mock(return_value=None)
        self.assertRaises(errors.ServiceNotFound,
                          analytics_controller.get_metrics_by_domain,
                          self.project_id, self.domain_name, **extras)

    def test_analytics_get_metrics_by_domain_provider_not_found(self):
        analytics_controller = \
            self.manager.analytics_controller
        extras = {}
        storage_controller = \
            self.manager.analytics_controller._driver.storage

        actual_provider_details = mock.Mock()
        actual_provider_details.get_domain_access_url = \
            mock.Mock(return_value=None)
        provider_details_dict = {
            'Provider': actual_provider_details
        }
        services_controller = storage_controller.services_controller
        services_controller.get_service_details_by_domain_name = \
            mock.Mock(return_value=StorageResult(
                provider_details=provider_details_dict))
        self.assertRaises(errors.ProviderDetailsIncomplete,
                          analytics_controller.get_metrics_by_domain,
                          self.project_id, self.domain_name, **extras)

    def test_analytics_get_metrics_by_domain_happy_path(self):

        analytics_controller = \
            self.manager.analytics_controller
        extras = {}
        storage_controller = \
            self.manager.analytics_controller._driver.storage

        actual_provider_details = mock.Mock()
        actual_provider_details.get_domain_access_url = \
            mock.Mock(return_value=self.domain_name)
        provider_details_dict = {
            'Mock_Provider': actual_provider_details
        }
        services_controller = storage_controller.services_controller
        services_controller.get_service_details_by_domain_name = \
            mock.Mock(return_value=StorageResult(
                provider_details=provider_details_dict,
                flavor_id='mock_flavor'))

        results = analytics_controller.get_metrics_by_domain(self.project_id,
                                                             self.domain_name,
                                                             **extras)

        self.assertEqual(results['provider'], 'mock_provider')
        self.assertEqual(results['flavor'], 'mock_flavor')
