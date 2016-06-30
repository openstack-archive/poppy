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
import uuid
try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

import ddt
import mock
from oslo_config import cfg
import testtools

from poppy.model.helpers import provider_details
from poppy.storage.cassandra import driver
from poppy.storage.cassandra import services
from poppy.transport.pecan.models.request import service as req_service
from tests.unit import base


@ddt.ddt
class CassandraStorageServiceTests(base.TestCase):

    def setUp(self):
        super(CassandraStorageServiceTests, self).setUp()

        # mock arguments to use
        self.project_id = '123456'
        self.service_id = uuid.uuid4()
        self.service_name = 'mocksite'

        # create mocked config and driver
        conf = cfg.ConfigOpts()
        conf.register_opt(
            cfg.StrOpt(
                'datacenter',
                default='',
                help='datacenter where the C* cluster hosted'))
        conf.register_opts(driver.CASSANDRA_OPTIONS,
                           group=driver.CASSANDRA_GROUP)
        cassandra_driver = driver.CassandraStorageDriver(conf)

        migrations_patcher = mock.patch(
            'cdeploy.migrator.Migrator'
        )
        migrations_patcher.start()
        self.addCleanup(migrations_patcher.stop)

        cluster_patcher = mock.patch('cassandra.cluster.Cluster')
        self.mock_cluster = cluster_patcher.start()
        self.mock_session = self.mock_cluster().connect()
        self.addCleanup(cluster_patcher.stop)

        # stubbed cassandra driver
        self.sc = services.ServicesController(cassandra_driver)

    @ddt.file_data('data_get_service.json')
    def test_get_service(self, value):

        # mock the response from cassandra
        value[0]['service_id'] = self.service_id
        self.mock_session.execute.return_value = value

        actual_response = self.sc.get_service(self.project_id, self.service_id)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(str(actual_response.service_id), str(self.service_id))

    @ddt.file_data('data_get_service.json')
    def test_update_state(self, value):

        details = value[0]['provider_details']
        new_details = {}
        for provider, detail in list(details.items()):
            detail = json.loads(detail)
            detail['status'] = 'deployed'
            detail['access_urls'] = [
                {
                    'provider_url': "{0}.com".format(provider.lower()),
                    'domain': detail['access_urls'][0]
                }
            ]
            new_details[provider] = json.dumps(detail)

        value[0]['provider_details'] = new_details
        # mock the response from cassandra
        value[0]['service_id'] = self.service_id
        self.mock_session.execute.return_value = [value[0]]

        expected_obj = self.sc.get_service(self.project_id, self.service_id)

        actual_obj = self.sc.update_state(self.project_id, self.service_id,
                                          'deployed')

        self.assertEqual(expected_obj.service_id, actual_obj.service_id)

    def test_get_service_with_exception(self):

        # mock the response from cassandra
        self.mock_session.execute.return_value = []

        self.assertRaises(
            ValueError,
            self.sc.get_service,
            self.project_id,
            self.service_id
        )

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=False)
    def test_create_service(self, value, mock_check):
        service_obj = req_service.load_from_json(value)
        responses = self.sc.create_service(self.project_id, service_obj)

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(responses, None)

        # TODO(amitgandhinz): need to validate the create to cassandra worked.

    @ddt.file_data('../data/data_create_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=True)
    def test_create_service_exist(self, value, mock_check):
        service_obj = req_service.load_from_json(value)
        self.sc.get = mock.Mock(return_value=service_obj)

        self.assertRaises(
            ValueError,
            self.sc.create_service,
            self.project_id, service_obj
        )

    @ddt.file_data('data_list_services.json')
    def test_list_services(self, value):
        # mock the response from cassandra
        value[0]['project_id'] = self.project_id
        self.mock_session.prepare.return_value = mock.Mock()
        self.mock_session.execute.return_value = value

        actual_response = self.sc.get_services(self.project_id, None, None)

        # TODO(amitgandhinz): assert the response
        # matches the expectation (using jsonschema)
        self.assertEqual(actual_response[0].name, "mocksite")
        self.assertEqual(actual_response[0].project_id, self.project_id)

    @ddt.file_data('data_get_service.json')
    def test_delete_service(self, value):

        details = value[0]['provider_details']
        new_details = {}
        for provider, detail in list(details.items()):
            detail = json.loads(detail)
            detail['status'] = 'deployed'
            detail['access_urls'] = [
                {
                    'provider_url': "{0}.com".format(provider.lower()),
                    'domain': detail['access_urls'][0]
                }
            ]
            new_details[provider] = json.dumps(detail)

        value[0]['provider_details'] = new_details

        # mock the response from cassandra
        value[0]['service_id'] = self.service_id
        # self.mock_session.execute.return_value = value

        def mock_execute_side_effect(*args):
            if args[0].query_string == services.CQL_GET_SERVICE:
                return [value[0]]
            else:
                return None

        self.mock_session.execute.side_effect = mock_execute_side_effect

        self.sc.delete_service(
            self.project_id,
            self.service_id
        )
        # TODO(isaacm): Add assertions on queries called

    def test_delete_service_no_result(self):
        # mock the response from cassandra
        self.mock_session.execute.return_value = iter([{}])
        actual_response = self.sc.delete_service(
            self.project_id,
            self.service_id
        )

        # Expect the response to be None as there are no providers passed
        # into the driver to respond to this call
        self.assertEqual(actual_response, None)

    @ddt.file_data('../data/data_update_service.json')
    @mock.patch.object(services.ServicesController,
                       'domain_exists_elsewhere',
                       return_value=False)
    @mock.patch.object(services.ServicesController,
                       'set_service_provider_details')
    def test_update_service(self, service_json,
                            mock_set_service_provider_details,
                            mock_check):
            with mock.patch.object(
                    services.ServicesController,
                    'get_provider_details') as mock_provider_det:

                mock_provider_det.return_value = {
                    "MaxCDN": "{\"id\": 11942, \"access_urls\": "
                              "[{\"provider_url\": \"maxcdn.provider.com\", "
                              "\"domain\": \"xk.cd\"}], "
                              "\"domains_certificate_status\":"
                              "{\"mypullzone.com\": "
                              "\"failed\"} }",
                }
                self.mock_session.execute.return_value = iter([{}])
                service_obj = req_service.load_from_json(service_json)
                actual_response = self.sc.update_service(
                    self.project_id,
                    self.service_id,
                    service_obj
                )

                # Expect the response to be None as there are no
                # providers passed into the driver to respond to this call
                self.assertEqual(actual_response, None)

    @ddt.file_data('data_provider_details.json')
    def test_get_provider_details(self, provider_details_json):
        # mock the response from cassandra
        self.mock_session.execute.return_value = [
            {'provider_details': provider_details_json}
        ]
        actual_response = self.sc.get_provider_details(
            self.project_id,
            self.service_id
        )
        self.assertTrue("MaxCDN" in actual_response)
        self.assertTrue("Mock" in actual_response)
        self.assertTrue("CloudFront" in actual_response)
        self.assertTrue("Fastly" in actual_response)

    @ddt.file_data('data_provider_details.json')
    def test_get_provider_details_value_error(self, provider_details_json):
        # mock the response from cassandra
        self.mock_session.execute.return_value = []

        with testtools.ExpectedException(ValueError):
            self.sc.get_provider_details(
                self.project_id,
                self.service_id
            )

    @ddt.file_data('data_provider_details.json')
    def test_update_provider_details(self, provider_details_json):
        provider_details_dict = {}
        for k, v in provider_details_json.items():
            provider_detail_dict = json.loads(v)

            provider_details_dict[k] = provider_details.ProviderDetail(
                provider_service_id=(
                    provider_detail_dict["id"]),
                access_urls=provider_detail_dict["access_urls"],
                domains_certificate_status=provider_detail_dict.get(
                    "domains_certificate_status", {}))

        # mock the response from cassandra
        self.mock_session.execute.return_value = None

        # this is for update_provider_details unittest code coverage
        arg_provider_details_dict = {}
        status = None
        for provider_name in provider_details_dict:
            the_provider_detail_dict = collections.OrderedDict()
            the_provider_detail_dict["id"] = (
                provider_details_dict[provider_name].provider_service_id)
            the_provider_detail_dict["access_urls"] = (
                provider_details_dict[provider_name].access_urls)
            the_provider_detail_dict["status"] = (
                provider_details_dict[provider_name].status)
            status = the_provider_detail_dict["status"]
            the_provider_detail_dict["name"] = (
                provider_details_dict[provider_name].name)
            the_provider_detail_dict["domains_certificate_status"] = (
                provider_details_dict[provider_name].
                domains_certificate_status.to_dict())
            the_provider_detail_dict["error_info"] = (
                provider_details_dict[provider_name].error_info)
            the_provider_detail_dict["error_message"] = (
                provider_details_dict[provider_name].error_message)
            arg_provider_details_dict[provider_name] = json.dumps(
                the_provider_detail_dict)

        provider_details_args = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'provider_details': arg_provider_details_dict
        }
        status_args = {
            'status': status,
            'project_id': self.project_id,
            'service_id': self.service_id
        }
        # This is to verify mock has been called with the correct arguments

        def assert_mock_execute_args(*args):

            if args[0].query_string == services.CQL_UPDATE_PROVIDER_DETAILS:
                self.assertEqual(args[1], provider_details_args)
            elif args[0].query_string == services.CQL_SET_SERVICE_STATUS:
                self.assertEqual(args[1], status_args)

        self.mock_session.execute.side_effect = assert_mock_execute_args

        with mock.patch.object(
                services.ServicesController,
                'get_provider_details') as mock_provider_det:

            mock_provider_det.return_value = {
                "MaxCDN":  # "{\"id\": 11942, \"access_urls\": "
                #           "[{\"provider_url\": \"maxcdn.provider.com\", "
                #           "\"domain\": \"xk.cd\"}], "
                #           "\"domains_certificate_status\":"
                #           "{\"mypullzone.com\": "
                #           "\"failed\"} }",
                provider_details.ProviderDetail(
                    provider_service_id='{}',
                    access_urls=[]
                )
            }

            self.sc.update_provider_details(
                self.project_id,
                self.service_id,
                provider_details_dict
            )

    @ddt.file_data('data_provider_details.json')
    def test_update_provider_details_domain_deleted(
            self,
            provider_details_json,
    ):
        provider_details_dict = {}
        for k, v in provider_details_json.items():
            provider_detail_dict = json.loads(v)

            provider_details_dict[k] = provider_details.ProviderDetail(
                provider_service_id=(
                    provider_detail_dict["id"]),
                access_urls=provider_detail_dict["access_urls"],
                domains_certificate_status=provider_detail_dict.get(
                    "domains_certificate_status", {}))

        # mock the response from cassandra
        self.mock_session.execute.return_value = None

        # this is for update_provider_details unittest code coverage
        arg_provider_details_dict = {}
        status = None
        for provider_name in provider_details_dict:
            the_provider_detail_dict = collections.OrderedDict()
            the_provider_detail_dict["id"] = (
                provider_details_dict[provider_name].provider_service_id)
            the_provider_detail_dict["access_urls"] = (
                provider_details_dict[provider_name].access_urls)
            the_provider_detail_dict["status"] = (
                provider_details_dict[provider_name].status)
            status = the_provider_detail_dict["status"]
            the_provider_detail_dict["name"] = (
                provider_details_dict[provider_name].name)
            the_provider_detail_dict["domains_certificate_status"] = (
                provider_details_dict[provider_name].
                domains_certificate_status.to_dict())
            the_provider_detail_dict["error_info"] = (
                provider_details_dict[provider_name].error_info)
            the_provider_detail_dict["error_message"] = (
                provider_details_dict[provider_name].error_message)
            arg_provider_details_dict[provider_name] = json.dumps(
                the_provider_detail_dict)

        provider_details_args = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'provider_details': arg_provider_details_dict
        }
        status_args = {
            'status': status,
            'project_id': self.project_id,
            'service_id': self.service_id
        }
        # This is to verify mock has been called with the correct arguments

        def assert_mock_execute_args(*args):

            if args[0].query_string == services.CQL_UPDATE_PROVIDER_DETAILS:
                self.assertEqual(args[1], provider_details_args)
            elif args[0].query_string == services.CQL_SET_SERVICE_STATUS:
                self.assertEqual(args[1], status_args)

        self.mock_session.execute.side_effect = assert_mock_execute_args

        with mock.patch.object(
                services.ServicesController,
                'get_provider_details') as mock_provider_det:

            mock_provider_det.return_value = {
                "MaxCDN": provider_details.ProviderDetail(
                    provider_service_id=(
                        "{\"id\": 11942, \"access_urls\": "
                        "[{\"provider_url\": \"maxcdn.provider.com\", "
                        "\"domain\": \"xk2.cd\"}], "
                        "\"domains_certificate_status\":"
                        "{\"mypullzone.com\": "
                        "\"failed\"} }"
                    ),
                    access_urls=[
                        {
                            "provider_url": "fastly.provider.com",
                            "domain": "xk2.cd"
                        }
                    ]
                )
            }

            self.sc.update_provider_details(
                self.project_id,
                self.service_id,
                provider_details_dict
            )

            delete_queries = []
            deleted_domains = []
            for query_mock_call in self.sc.session.execute.mock_calls:
                name, args, kwargs = query_mock_call
                for arg in args:
                    if hasattr(arg, 'query_string'):
                        if (
                            arg.query_string ==
                            services.CQL_DELETE_PROVIDER_URL
                        ):
                            delete_queries.append(query_mock_call)
                            _, delete_query_args = args
                            deleted_domains.append(
                                delete_query_args["domain_name"])

            self.assertEqual(1, len(delete_queries))
            self.assertEqual(['xk2.cd'], deleted_domains)

            self.assertTrue(self.sc.session.execute.called)

    def test_update_provider_details_new_provider_details_empty(self):

        provider_details_dict = {}

        # mock the response from cassandra
        self.mock_session.execute.return_value = None

        # this is for update_provider_details unittest code coverage
        arg_provider_details_dict = {}
        status = None

        provider_details_args = {
            'project_id': self.project_id,
            'service_id': self.service_id,
            'provider_details': arg_provider_details_dict
        }
        status_args = {
            'status': status,
            'project_id': self.project_id,
            'service_id': self.service_id
        }
        # This is to verify mock has been called with the correct arguments

        def assert_mock_execute_args(*args):

            if args[0].query_string == services.CQL_UPDATE_PROVIDER_DETAILS:
                self.assertEqual(args[1], provider_details_args)
            elif args[0].query_string == services.CQL_SET_SERVICE_STATUS:
                self.assertEqual(args[1], status_args)

        self.mock_session.execute.side_effect = assert_mock_execute_args

        with mock.patch.object(
                services.ServicesController,
                'get_provider_details') as mock_provider_det:

            mock_provider_det.return_value = {
                "MaxCDN": provider_details.ProviderDetail(
                    provider_service_id=(
                        "{\"id\": 11942, \"access_urls\": "
                        "[{\"provider_url\": \"maxcdn.provider.com\", "
                        "\"domain\": \"xk2.cd\"}], "
                        "\"domains_certificate_status\":"
                        "{\"mypullzone.com\": "
                        "\"failed\"} }"
                    ),
                    access_urls=[
                        {
                            "provider_url": "fastly.provider.com",
                            "domain": "xk2.cd"
                        }
                    ]
                )
            }

            self.sc.update_provider_details(
                self.project_id,
                self.service_id,
                provider_details_dict
            )

            delete_queries = []
            deleted_domains = []
            for query_mock_call in self.sc.session.execute.mock_calls:
                name, args, kwargs = query_mock_call
                for arg in args:
                    if hasattr(arg, 'query_string'):
                        if (
                            arg.query_string ==
                            services.CQL_DELETE_PROVIDER_URL
                        ):
                            delete_queries.append(query_mock_call)
                            _, delete_query_args = args
                            deleted_domains.append(
                                delete_query_args["domain_name"])

            self.assertEqual(1, len(delete_queries))
            self.assertEqual(['xk2.cd'], deleted_domains)

            self.assertTrue(self.sc.session.execute.called)

    def test_session(self):
        session = self.sc.session
        self.assertNotEqual(session, None)

    def test_domain_exists_elsewhere_true(self):
        self.mock_session.execute.return_value = [
            {
                'service_id': 'service_id',
                'project_id': 'project_id',
                'domain_name': 'domain_name'
            }
        ]
        self.assertTrue(
            self.sc.domain_exists_elsewhere('domain_name', 'new_service_id'))

    def test_domain_exists_elsewhere_false(self):
        self.mock_session.execute.return_value = [
            {
                'service_id': 'service_id',
                'project_id': 'project_id',
                'domain_name': 'domain_name'
            }
        ]
        self.assertFalse(
            self.sc.domain_exists_elsewhere('domain_name', 'service_id'))

    def test_domain_exists_elsewhere_no_results(self):
        self.mock_session.execute.return_value = []
        self.assertFalse(
            self.sc.domain_exists_elsewhere('domain_name', 'new_service_id'))

    def test_domain_exists_elsewhere_value_error(self):
        self.mock_session.execute.side_effect = ValueError(
            'Mock -- Something went wrong!'
        )
        self.assertFalse(
            self.sc.domain_exists_elsewhere('domain_name', 'new_service_id'))

    def test_get_service_count_positive(self):

        self.mock_session.execute.return_value = [
            {
                'count': 1
            }
        ]

        self.assertEqual(1, self.sc.get_service_count('project_id'))

    @ddt.file_data('data_list_services.json')
    def test_get_services_marker_not_none(self, data):

        self.mock_session.execute.return_value = data

        results = self.sc.get_services('project_id', uuid.uuid4(), 1)
        self.assertEqual(data[0]["project_id"], results[0].project_id)

    def test_get_services_by_status_positive(self):

        self.mock_session.execute.return_value = [
            {'service_id': 1},
            {'service_id': 2},
            {'service_id': 3}
        ]

        self.assertEqual(
            [
                {'service_id': '1'},
                {'service_id': '2'},
                {'service_id': '3'}
            ],
            self.sc.get_services_by_status('project_id')
        )

    def test_delete_services_by_status_positive(self):
        try:
            self.sc.delete_services_by_status(
                'project_id', uuid.uuid4(), 'status'
            )
        except Exception as e:
            self.fail(e)

    def test_get_domains_by_provider_url_positive(self):

        self.mock_session.execute.return_value = [
            {'domain_name': 'www.xyz.com'},
        ]

        self.assertEqual([{'domain_name': 'www.xyz.com'}],
                         self.sc.get_domains_by_provider_url('provider_url'))

    def test_delete_provider_url_positive(self):
        try:
            self.sc.delete_provider_url('provider_url', 'domain_name')
        except Exception as e:
            self.fail(e)

    def test_get_service_limit_positive(self):
        self.mock_session.execute.return_value = [
            {'project_limit': 999}
        ]
        self.assertEqual(999, self.sc.get_service_limit('project_id'))

    def test_get_service_limit_empty_result(self):
        self.mock_session.execute.return_value = []

        self.assertEqual(
            self.sc._driver.max_services_conf.max_services_per_project,
            self.sc.get_service_limit('project_id'))

    def test_get_service_limit_value_error(self):
        self.mock_session.execute.side_effect = ValueError(
            'Mock -- Something went wrong!'
        )
        self.assertEqual(
            self.sc._driver.max_services_conf.max_services_per_project,
            self.sc.get_service_limit('project_id')
        )

    def test_set_service_limit_positive(self):
        try:
            self.sc.set_service_limit('project_id', 'project_limit')
        except Exception as e:
            self.fail(e)

    @ddt.file_data('data_list_services.json')
    def test_get_service_details_by_domain_name(self, data):
        service_id = uuid.uuid4()
        self.mock_session.execute.side_effect = [
            [{
                'project_id': 'project_id',
                'service_id': service_id,
                'domain_name': 'domain_name'
            }],
            [data[0]]
        ]

        results = self.sc.get_service_details_by_domain_name('domain_name')

        self.assertEqual(data[0]["project_id"], results.project_id)

    @ddt.file_data('data_list_services.json')
    def test_get_service_details_by_domain_name_domain_not_present(
            self, data):
        self.mock_session.execute.side_effect = [
            [{
                'project_id': 'proj_id',  # differs from arg to func
                'service_id': uuid.uuid4(),
                'domain_name': 'domain_name'
            }],
            [data[0]]
        ]

        with testtools.ExpectedException(ValueError):
            self.sc.get_service_details_by_domain_name(
                'domain_name',
                project_id='project_id'
            )

    @ddt.file_data('data_provider_details.json')
    def test_set_service_provider_details(self, data):
        service_id = uuid.uuid4()

        def mock_execute_side_effect(*args):
            if args[0].query_string == services.CQL_GET_PROVIDER_DETAILS:
                return [{'provider_details': data}]
            else:
                return None

        self.mock_session.execute.side_effect = mock_execute_side_effect

        self.sc.set_service_provider_details(
            'project_id', service_id, 'deployed'
        )

        [
            update_service_status,
            get_provider_details,
            _,
            update_provider_details,
            _,
            _,
            _,
            _,
            _,
        ] = self.mock_session.execute.mock_calls

        self.assertEqual(services.CQL_SET_SERVICE_STATUS,
                         update_service_status[1][0].query_string)
        self.assertEqual(services.CQL_GET_PROVIDER_DETAILS,
                         get_provider_details[1][0].query_string)
        self.assertEqual(services.CQL_UPDATE_PROVIDER_DETAILS,
                         update_provider_details[1][0].query_string)
