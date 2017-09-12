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


from poppy.manager.default import background_job
from poppy.manager.default import driver
from poppy.model.helpers import domain
from poppy.model import service
from poppy.notification.mailgun import driver as n_driver
from poppy.provider.akamai import driver as aka_driver
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
        conf.register_opts(aka_driver.AKAMAI_OPTIONS, aka_driver.AKAMAI_GROUP)
        conf.register_opts(n_driver.MAIL_NOTIFICATION_OPTIONS,
                           n_driver.MAIL_NOTIFICATION_GROUP)
        conf.set_override(
            'san_cert_cnames',
            [
                "san.example.com", "san2.example.com"
            ],
            group=aka_driver.AKAMAI_GROUP
        )
        self.addCleanup(
            conf.clear_override,
            'san_cert_cnames',
            group=aka_driver.AKAMAI_GROUP
        )
        conf.set_override(
            'sni_cert_cnames',
            [
                "sni.example.com", "sni2.example.com"
            ],
            group=aka_driver.AKAMAI_GROUP
        )
        self.addCleanup(
            conf.clear_override,
            'sni_cert_cnames',
            group=aka_driver.AKAMAI_GROUP
        )
        conf.set_override(
            'akamai_https_access_url_suffix',
            'edge.key.net',
            group=aka_driver.AKAMAI_GROUP
        )
        self.addCleanup(
            conf.clear_override,
            'akamai_https_access_url_suffix',
            group=aka_driver.AKAMAI_GROUP
        )

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
            obj_mock.san_cert_cnames = ["san.example.com", "san2.example.com"]
            obj_mock.akamai_sps_api_base_url = 'akamai_base_url/{spsId}'

            provider = mock.Mock(obj=obj_mock)
            return provider

        def provider_membership(key):
            return True if key in self.provider_mocks else False

        self.mock_storage = mock_storage
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
        self.bgc = background_job.BackgroundJobController(
            self.manager_driver
        )

    def test_get_san_mapping_list_positive(self):
        self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            })
        ]

        self.assertEqual(1, len(self.bgc.get_san_mapping_list()))

    def test_get_san_mapping_list_no_akamai_provider(self):
        del self.provider_mocks['akamai']

        self.assertEqual(0, len(self.bgc.get_san_mapping_list()))

    def test_put_san_mapping_list_no_akamai_provider(self):
        del self.provider_mocks['akamai']
        new_queue_data = [
            {
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            }
        ]
        res, deleted = self.bgc.put_san_mapping_list(new_queue_data)
        self.assertEqual(0, len(res))
        self.assertEqual(0, len(deleted))

    def test_put_san_mapping_list(self):
        original_queue_data = [{
            "domain_name": "www.example.com",
            "flavor_id": "flavor_id",
            "project_id": "project_id",
            "cert_type": "san",
            "cert_details": {
                "Akamai": {
                    "extra_info": {
                        "san cert": "san.example.com",
                        "akamai_spsId": 1
                    }
                }
            }
        }]

        akamai_driver = self.manager_driver.providers[
            'akamai'].obj
        akamai_driver.san_mapping_queue.traverse_queue.return_value = [
            json.dumps(original_queue_data)
        ]
        akamai_driver.san_mapping_queue.put_queue_data.side_effect = lambda \
            value: value

        new_queue_data = [{
            "domain_name": "new.example.com",
            "flavor_id": "flavor_id",
            "project_id": "project_id",
            "cert_type": "san",
            "cert_details": {
                "Akamai": {
                    "extra_info": {
                        "san cert": "san.example.com",
                        "akamai_spsId": 1
                    }
                }
            }
        }]

        res, deleted = self.bgc.put_san_mapping_list(new_queue_data)

        self.assertEqual(new_queue_data, res)

        self.assertTrue(
            akamai_driver.san_mapping_queue.traverse_queue.called
        )
        self.assertTrue(
            akamai_driver.san_mapping_queue.put_queue_data.called
        )

    @ddt.data(
        "akamai_check_and_update_cert_status",
        "akamai_update_papi_property_for_mod_san",
        "akamai_update_papi_property_for_mod_sni"
    )
    def test_post_job_no_akamai_driver(self, job_type):
        del self.provider_mocks['akamai']

        run_list, ignore_list = self.bgc.post_job(job_type, {})

        self.assertEqual(0, len(run_list))
        self.assertEqual(0, len(ignore_list))

    @ddt.data(
        ("akamai_check_and_update_cert_status", "san"),
        ("akamai_update_papi_property_for_mod_san", "san"),
        ("akamai_update_papi_property_for_mod_sni", "sni")
    )
    def test_post_job_positive(self, job_tuple):
        job_type, cert_type = job_tuple
        # mock ssl storage returning a cert
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = [
                mock.Mock()
            ]
        # mock service storage returning a service with domain with
        # correct protocol + cert
        self.mock_storage.services_controller. \
            get_service_details_by_domain_name.return_value = service.Service(
                'service_id',
                'name',
                [
                    domain.Domain(
                        "www.example.com",
                        protocol='https',
                        certificate=cert_type
                    )
                ],
                [],
                'flavor_id',
                project_id='project_id'
            )

        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "{0}.example.com".format(cert_type),
                            "akamai_spsId": 1
                        }
                    }
                },
                'property_activated': (
                    True
                    if job_type == "akamai_check_and_update_cert_status"
                    else False)
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            job_type,
            {'project_id': 'project_id'}
        )
        self.assertEqual(1, len(run_list))
        self.assertEqual(0, len(ignore_list))

        self.assertTrue(
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data(
        ("akamai_update_papi_property_for_mod_san", "san"),
        ("akamai_update_papi_property_for_mod_sni", "sni")
    )
    def test_post_job_skip_activated(self, job_tuple):
        job_type, cert_type = job_tuple
        # mock ssl storage returning a cert
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = [
                mock.Mock()
            ]
        # mock service storage returning a service with domain with
        # correct protocol + cert
        self.mock_storage.services_controller. \
            get_service_details_by_domain_name.return_value = service.Service(
                'service_id',
                'name',
                [
                    domain.Domain(
                        "www.example.com",
                        protocol='https',
                        certificate=cert_type
                    )
                ],
                [],
                'flavor_id',
                project_id='project_id'
            )

        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "{0}.example.com".format(cert_type),
                            "akamai_spsId": 1
                        }
                    }
                },
                # This item will be skipped if repeated attempts
                # to activate the same domain_name are made.
                "property_activated": True
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            job_type,
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertFalse(
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data("san", "sni")
    def test_post_job_ignored_cert_no_longer_exists(self, cert_type):
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = []
        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                },
                'property_activated': True
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            "akamai_update_papi_property_for_mod_{0}".format(cert_type),
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            False,
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data("san", "sni")
    def test_post_job_domain_type_modified_on_service(self, cert_type):
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = [
                mock.Mock()
            ]
        # simulate domain being changed from https+san to http
        self.mock_storage.services_controller. \
            get_service_details_by_domain_name.return_value = service.Service(
                'service_id',
                'name',
                [
                    domain.Domain(
                        "www.example.com",
                        protocol='http',
                    )
                ],
                [],
                'flavor_id',
                project_id='project_id'
            )
        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                },
                'property_activated': True
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            "akamai_update_papi_property_for_mod_{0}".format(cert_type),
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            False,
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data("san", "sni")
    def test_post_job_service_no_longer_exists(self, cert_type):
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = [
                mock.Mock()
            ]
        # simulate domain being changed from https+san to http
        self.mock_storage.services_controller. \
            get_service_details_by_domain_name.return_value = None

        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                },
                'property_activated': True
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            "akamai_update_papi_property_for_mod_{0}".format(cert_type),
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            False,
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data(
        ("akamai_update_papi_property_for_mod_san", "san"),
        ("akamai_update_papi_property_for_mod_sni", "sni"),
    )
    def test_post_job_invalid_cert_cname(self, job_tuple):
        job_type, cert_type = job_tuple
        # mock ssl storage returning a cert
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = [
                mock.Mock()
            ]
        # mock service storage returning a service with domain with
        # correct protocol + cert
        self.mock_storage.services_controller. \
            get_service_details_by_domain_name.return_value = service.Service(
                'service_id',
                'name',
                [
                    domain.Domain(
                        "www.example.com",
                        protocol='https',
                        certificate=cert_type
                    )
                ],
                [],
                'flavor_id',
                project_id='project_id'
            )
        cert_key = ('san cert' if cert_type == 'san' else 'sni_cert')
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": cert_type,
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            cert_key: "not.exist.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            })
        ]

        run_list, ignore_list = self.bgc.post_job(
            job_type,
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            False,
            self.bgc.distributed_task_controller.submit_task.called
        )

    @ddt.data("akamai_check_and_update_cert_status")
    def test_post_job_submit_task_exception(self, job_type):
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                }
            })
        ]

        self.bgc.distributed_task_controller.submit_task.side_effect = (
            Exception('Mock -- Something went wrong submit_task()!')
        )
        run_list, ignore_list = self.bgc.post_job(
            job_type,
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            True,
            san_mapping_queue.enqueue_san_mapping.called
        )

    @ddt.data("akamai_check_and_update_cert_status")
    def test_post_job_submit_task_exception_enqueue_retry(self, job_type):
        san_mapping_queue = self.manager_driver.providers[
            'akamai'].obj.san_mapping_queue
        san_mapping_queue.traverse_queue.return_value = [
            json.dumps({
                "domain_name": "www.example.com",
                "flavor_id": "flavor_id",
                "project_id": "project_id",
                "cert_type": "san",
                "cert_details": {
                    "Akamai": {
                        "extra_info": {
                            "san cert": "san.example.com",
                            "akamai_spsId": 1
                        }
                    }
                },
                'property_activated': True
            })
        ]

        self.bgc.distributed_task_controller.submit_task.side_effect = (
            Exception('Mock -- Something went wrong submit_task()!')
        )
        san_mapping_queue.enqueue_san_mapping.side_effect = [
            Exception('Mock -- First enqueue attempt failed!'),
            None  # successful call on second attempt
        ]

        run_list, ignore_list = self.bgc.post_job(
            job_type,
            {'project_id': 'project_id'}
        )
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))

        self.assertEqual(
            True,
            san_mapping_queue.enqueue_san_mapping.called
        )

    def test_delete_http_policy_positive(self):
        cert_mock = mock.Mock()
        cert_mock.get_cert_status.return_value = 'deployed'
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = cert_mock

        http_policy_queue = self.manager_driver.providers[
            'akamai'].obj.http_policy_queue
        http_policy_queue.traverse_queue.return_value = [
            json.dumps({
                'policy_name': 'www.example.com',
                'project_id': 'project_id',
                'configuration_number': 12345
            })
        ]

        run_list, ignore_list = self.bgc.delete_http_policy()
        self.assertEqual(1, len(run_list))
        self.assertEqual(0, len(ignore_list))
        self.assertTrue(
            self.bgc.distributed_task_controller.submit_task.called
        )

    def test_delete_http_policy_cert_not_deployed(self):
        cert_mock = mock.Mock()
        cert_mock.get_cert_status.return_value = 'create_in_progress'
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = cert_mock

        http_policy_queue = self.manager_driver.providers[
            'akamai'].obj.http_policy_queue
        http_policy_queue.traverse_queue.return_value = [
            json.dumps({
                'policy_name': 'www.example.com',
                'project_id': 'project_id',
                'configuration_number': 12345
            })
        ]

        run_list, ignore_list = self.bgc.delete_http_policy()
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))
        self.assertFalse(
            self.bgc.distributed_task_controller.submit_task.called
        )

    def test_delete_http_policy_cert_doesnt_exist(self):
        self.mock_storage.certificates_controller.\
            get_certs_by_domain.return_value = []

        http_policy_queue = self.manager_driver.providers[
            'akamai'].obj.http_policy_queue
        http_policy_queue.traverse_queue.return_value = [
            json.dumps({
                'policy_name': 'www.example.com',
                'project_id': 'project_id',
                'configuration_number': 12345
            })
        ]

        run_list, ignore_list = self.bgc.delete_http_policy()
        self.assertEqual(0, len(run_list))
        self.assertEqual(1, len(ignore_list))
        self.assertFalse(
            self.bgc.distributed_task_controller.submit_task.called
        )

    def test_delete_http_policy_no_akamai_provider(self):
        del self.provider_mocks['akamai']

        run_list, ignore_list = self.bgc.delete_http_policy()
        self.assertEqual(0, len(run_list))
        self.assertEqual(0, len(ignore_list))
