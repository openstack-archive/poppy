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

import datetime
import json
import time
import uuid

import ddt
import mock

from poppy.model.helpers import cachingrule
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import restriction
from poppy.model.helpers import rule
from poppy.model.service import Service
from poppy.provider.akamai import geo_zone_code_mapping
from poppy.provider.akamai import services
from poppy.transport.pecan.models.request import service
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch(
        'poppy.provider.akamai.services.ServiceController.policy_api_client')
    @mock.patch(
        'poppy.provider.akamai.services.ServiceController.ccu_api_client')
    @mock.patch('poppy.provider.akamai.driver.CDNProvider')
    def setUp(
        self,
        mock_driver,
        mock_controller_ccu_api_client,
        mock_controller_policy_api_client
    ):
        super(TestServices, self).setUp()
        self.driver = mock_driver()
        self.driver.provider_name = 'Akamai'
        self.driver.akamai_https_access_url_suffix = str(uuid.uuid1())
        self.san_cert_cnames = [str(x) for x in range(7)]
        self.driver.san_cert_cnames = self.san_cert_cnames
        self.driver.regions = geo_zone_code_mapping.REGIONS
        self.driver.metrics_resolution = 86400
        self.controller = services.ServiceController(self.driver)
        service_id = str(uuid.uuid4())
        domains_old = domain.Domain(domain='cdn.poppy.org')
        current_origin = origin.Origin(origin='poppy.org')
        self.service_obj = Service(service_id=service_id,
                                   name='poppy cdn service',
                                   domains=[domains_old],
                                   origins=[current_origin],
                                   flavor_id='cdn')

    @ddt.file_data('domains_list.json')
    def test_classify_domains(self, domains_list):
        domains_list = [domain.Domain(domain_s) for domain_s in domains_list]
        c_domains_list = self.controller._classify_domains(domains_list)
        self.assertEqual(domains_list, c_domains_list, 'Domain list not equal'
                         ' classified domain list')

    @ddt.file_data('data_service.json')
    def test_create_with_exception(self, service_json):
        # ASSERTIONS
        # create_service
        service_obj = service.load_from_json(service_json)
        self.controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))
        self.controller.policy_api_client.put.side_effect = (
            RuntimeError('Creating service failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_get_sub_customer_exception(self, service_json):
        service_obj = service.load_from_json(service_json)
        self.controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=400,
                      ok=False,
                      content=json.dumps({"geo": "US"}))
        self.controller.policy_api_client.put.side_effect = (
            RuntimeError('Creating service failed.'))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_put_sub_customer_exception(self, service_json):
        # ASSERTIONS
        # create_service
        service_obj = service.load_from_json(service_json)
        self.controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=400,
                      ok=False,
                      content=json.dumps({"geo": "US"}))
        self.controller.subcustomer_api_client.put.return_value = \
            mock.Mock(status_code=400,
                      ok=False,
                      content=json.dumps({"geo": "US"}))
        resp = self.controller.create(service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_4xx_return(self, service_json):
        service_obj = service.load_from_json(service_json)
        self.controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))
        # test exception
        self.controller.policy_api_client.put.return_value = mock.Mock(
            status_code=400,
            text='Some create service error happened'
        )
        resp = self.controller.create(service_obj)

        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_service.json')
    def test_create_with_multiple_domains(self, service_json):
        service_obj = service.load_from_json(service_json)
        self.controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))
        self.controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        provider_responses = self.controller.create(service_obj)
        for provider_name in provider_responses:
            provider_response = provider_responses[provider_name]
            num_of_domains = len(service_obj.domains)
            num_of_links = len(provider_response['links'])
            # make sure we have same number of domains and links
            self.assertEqual(num_of_domains, num_of_links)
            self.assertIn('id', provider_responses[provider_name])

    @ddt.file_data('data_service.json')
    def test_create(self, service_json):
        controller = services.ServiceController(self.driver)
        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )

        service_obj = service.load_from_json(service_json)
        resp = controller.create(service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_delete_with_exception(self):
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http',
                                           'certificate': None}])

        # test exception
        exception = RuntimeError('ding')
        self.controller.policy_api_client.delete.side_effect = exception
        resp = self.controller.delete(service_obj, provider_service_id)

        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_service_id_json_load_error(self):
        # This should trigger a json.loads error
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))

        provider_service_id = None
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text='Get successful'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )

        resp = controller.delete(service_obj, provider_service_id)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete_with_4xx_return(self):
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))

        provider_service_id = json.dumps([{'policy_name': current_domain,
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text='Get successful'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=400,
            text='error happened'
        )

        resp = controller.delete(service_obj, provider_service_id)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_delete(self):
        service_id = str(uuid.uuid4())
        current_domain = str(uuid.uuid1())
        domains_old = domain.Domain(domain=current_domain)
        current_origin = origin.Origin(origin='poppy.org')
        service_obj = Service(service_id=service_id,
                              name='poppy cdn service',
                              domains=[domains_old],
                              origins=[current_origin],
                              flavor_id='cdn',
                              project_id=str(uuid.uuid4()))

        provider_service_id = json.dumps([{'policy_name': current_domain,
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text='Get successful'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )

        resp = controller.delete(service_obj, provider_service_id)
        self.assertIn('id', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update_with_get_error(self, service_json):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http'}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=400,
            text='Some get error happened'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update_with_service_id_json_load_error(self, service_json):
        # This should trigger a json.loads error
        provider_service_id = None
        service_obj = service.load_from_json(service_json)
        resp = self.controller.update(
            provider_service_id, service_obj)
        self.assertIn('error', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update(self, service_json):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)
        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text=json.dumps(dict(rules=[]))
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    @ddt.file_data('data_update_service.json')
    def test_update_with_domain_protocol_change(self, service_json):
        provider_service_id = json.dumps([{'policy_name': "densely.sage.com",
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text=json.dumps(dict(rules=[]))
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    @ddt.file_data('data_upsert_service.json')
    def test_upsert(self, service_json):
        provider_service_id = json.dumps([{'policy_name': "densely.sage.com",
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=404,
            text='Service not found'
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        service_obj = service.load_from_json(service_json)
        resp = controller.update(
            provider_service_id, service_obj)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_purge_all(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)
        resp = controller.purge(provider_service_id,
                                service_obj=self.service_obj,
                                hard=True, purge_url=None)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge_with_service_id_json_load_error(self):
        provider_service_id = None
        controller = services.ServiceController(self.driver)
        resp = controller.purge(provider_service_id,
                                service_obj=self.service_obj,
                                hard=True, purge_url=None)
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge_with_ccu_exception(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'http',
                                           'certificate': None}])
        controller = services.ServiceController(self.driver)
        controller.ccu_api_client.post.return_value = mock.Mock(
            status_code=400,
            text="purge request post failed"
        )
        resp = controller.purge(provider_service_id,
                                service_obj=self.service_obj,
                                hard=True, purge_url='/img/abc.jpeg')
        self.assertIn('error', resp[self.driver.provider_name])

    def test_purge(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'https',
                                           'certificate': 'shared'}])
        controller = services.ServiceController(self.driver)
        controller.ccu_api_client.post.return_value = mock.Mock(
            status_code=201,
            text="purge request post complete"
        )
        purge_url = '/img/abc.jpeg'
        actual_purge_url = ("https://" +
                            json.loads(provider_service_id)[0]['policy_name']
                            + purge_url)
        data = {
            'objects': [
                actual_purge_url
            ]
        }
        resp = controller.purge(provider_service_id,
                                service_obj=self.service_obj,
                                hard=True, purge_url=purge_url)
        controller.ccu_api_client.post.assert_called_once_with(
            controller.ccu_api_base_url,
            data=json.dumps(data),
            headers=(
                controller.request_header
            ))
        self.assertIn('id', resp[self.driver.provider_name])

    def test_cache_invalidate(self):
        provider_service_id = json.dumps([{'policy_name': str(uuid.uuid1()),
                                           'protocol': 'https',
                                           'certificate': 'shared'}])
        controller = services.ServiceController(self.driver)

        controller.subcustomer_api_client.get.return_value = \
            mock.Mock(status_code=200,
                      ok=True,
                      content=json.dumps({"geo": "US"}))

        controller.subcustomer_api_client.delete.return_value = \
            mock.Mock(status_code=200,
                      ok=True)

        controller.policy_api_client.get.return_value = mock.Mock(
            status_code=200,
            text=json.dumps(dict(rules=[]))
        )
        controller.policy_api_client.put.return_value = mock.Mock(
            status_code=200,
            text='Put successful'
        )
        controller.policy_api_client.delete.return_value = mock.Mock(
            status_code=200,
            text='Delete successful'
        )
        purge_url = '/img/abc.jpeg'

        resp = controller.purge(provider_service_id,
                                service_obj=self.service_obj,
                                hard=False, purge_url=purge_url)
        self.assertIn('id', resp[self.driver.provider_name])

    def test_process_caching_rules(self):
        controller = services.ServiceController(self.driver)
        caching_rule_entry = rule.Rule('index', request_url='*.jpg')
        caching_rule = cachingrule.CachingRule('home',
                                               600,
                                               rules=[caching_rule_entry])
        caching_rules = [caching_rule]
        rules_list = [{
            'matches': [{
                'name': 'url-wildcard',
                'value': u'/*'
            }],
            'behaviors': [{
                'params': {
                    'hostHeaderValue': '-',
                    'cacheKeyType': 'digital_property',
                    'cacheKeyValue': '-',
                    'originDomain': 'www.mydomain.com',
                    'hostHeaderType': 'digital_property'
                },
                'name': 'origin',
                'value': '-'
            }]
        }]
        controller._process_caching_rules(caching_rules, rules_list)
        caching_rule_valid = False
        for caching_rule in rules_list:
            matches = caching_rule['matches']
            for match in matches:
                if match['value'] == u'/*.jpg':
                    caching_rule_valid = True
                    break

        self.assertTrue(caching_rule_valid)

    def test_process_origin_rule(self):
        controller = services.ServiceController(self.driver)
        rule_entry = rule.Rule('index', request_url='*.jpg')
        origin_rule = origin.Origin(origin='poppy.com', rules=[rule_entry])

        rules_list = [{
            'matches': [{
                'name': 'url-wildcard',
                'value': u'/*'
            }],
            'behaviors': [{
                'params': {
                    'hostHeaderValue': '-',
                    'cacheKeyType': 'digital_property',
                    'cacheKeyValue': '-',
                    'originDomain': 'www.mydomain.com',
                    'hostHeaderType': 'digital_property'
                },
                'name': 'origin',
                'value': '-'
            }]
        }]
        controller._process_new_origin(origin_rule, rules_list)
        origin_rule_valid = False
        for origin_rule in rules_list:
            matches = origin_rule['matches']
            for match in matches:
                if match['value'] == u'/*.jpg':
                    origin_rule_valid = True
                    break

        self.assertTrue(origin_rule_valid)

    def get_provider_service_id(self):
        controller = services.ServiceController(self.driver)
        provider_service_id = controller.get(self.service_obj)
        self.assertTrue(provider_service_id is not None)
        self.assertTrue(isinstance(provider_service_id, str))
        for domain_obj in self.service_obj.domains:
            self.assertTrue(domain_obj.domain in provider_service_id)

    def test_process_restriction_rules(self):
        controller = services.ServiceController(self.driver)
        rule_entry = rule.Rule('index',
                               request_url='*.jpg',
                               referrer='www.poppy.com')
        restriction_rule = restriction.Restriction(name='restriction',
                                                   rules=[rule_entry])

        restriction_rules = [restriction_rule]
        rules_list = [{
            'matches': [{
                'name': 'url-wildcard',
                'value': u'/*'
            }],
            'behaviors': [{
                'params': {
                    'hostHeaderValue': '-',
                    'cacheKeyType': 'digital_property',
                    'cacheKeyValue': '-',
                    'originDomain': 'www.mydomain.com',
                    'hostHeaderType': 'digital_property'
                },
                'name': 'origin',
                'value': '-'
            }]
        }]
        controller._process_restriction_rules(restriction_rules, rules_list)
        restriction_rule_valid = False
        for restriction_rule in rules_list:
            matches = restriction_rule['matches']
            for match in matches:
                if match['value'] == u'/*.jpg':
                    restriction_rule_valid = True
                    break

        self.assertTrue(restriction_rule_valid)

    def test_regions(self):
        controller = services.ServiceController(self.driver)
        self.assertEqual(controller.driver.regions,
                         geo_zone_code_mapping.REGIONS)

    @ddt.data('requestCount', 'bandwidthOut', 'httpResponseCode_1XX',
              'httpResponseCode_2XX', 'httpResponseCode_3XX',
              'httpResponseCode_4XX', 'httpResponseCode_5XX')
    def test_get_metrics_by_domain_metrics_controller(self, metrictype):
        controller = services.ServiceController(self.driver)
        project_id = str(uuid.uuid4())
        domain_name = 'www.' + str(uuid.uuid4()) + '.com'
        regions = controller.driver.regions
        end_time = datetime.datetime.utcnow()
        start_time = (datetime.datetime.utcnow() - datetime.timedelta(days=1))
        startTime = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        endTime = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        metrics_controller = mock.Mock()
        # NOTE(TheSriram): We mock a empty return value, to just test
        # what the call args were for the metrics_controller
        metrics_controller.read = mock.Mock(return_value=[])

        extras = {
            'metricType': metrictype,
            'startTime': startTime,
            'endTime': endTime,
            'metrics_controller': metrics_controller
        }

        controller.get_metrics_by_domain(project_id, domain_name,
                                         regions, **extras)

        call_args = metrics_controller.read.call_args[1]
        self.assertEqual(call_args['resolution'],
                         self.driver.metrics_resolution)
        self.assertEqual(call_args['to_timestamp'], endTime)
        self.assertEqual(call_args['from_timestamp'], startTime)
        metric_names = call_args['metric_names']
        for metric_name in metric_names:
            metric_split = metric_name.split('_')
            if len(metric_split) == 3:
                self.assertEqual(metric_split[0], metrictype)
                self.assertEqual(metric_split[1], domain_name)
                self.assertIn(metric_split[2], regions)
            else:
                self.assertEqual(metric_split[0], 'httpResponseCode')
                self.assertIn(metric_split[1], metrictype.split('_')[1])
                self.assertEqual(metric_split[2], domain_name)
                self.assertIn(metric_split[3], regions)

    @ddt.data('requestCount', 'bandwidthOut', 'httpResponseCode_1XX',
              'httpResponseCode_2XX', 'httpResponseCode_3XX',
              'httpResponseCode_4XX', 'httpResponseCode_5XX')
    def test_get_metrics_by_domain_metrics_controller_return(self, metrictype):
        controller = services.ServiceController(self.driver)
        project_id = str(uuid.uuid4())
        domain_name = 'www.' + str(uuid.uuid4()) + '.com'
        regions = ['NorthAmerica', 'SouthAmerica', 'EMEA', 'Japan', 'India',
                   'APAC']
        end_time = datetime.datetime.utcnow()
        start_time = (datetime.datetime.utcnow() - datetime.timedelta(days=1))
        startTime = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        endTime = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        metrics_controller = mock.Mock()
        metric_buckets = []

        if 'httpResponseCode' in metrictype:
            http_series = metrictype.split('_')[1]
            for region in regions:
                metric_buckets.append('_'.join(['httpResponseCode',
                                                http_series,
                                                domain_name,
                                                region]))
        else:
            for region in regions:
                metric_buckets.append('_'.join([metrictype, domain_name,
                                                region]))

        timestamp = str(int(time.time()))
        value = 55
        metrics_response = [(metric_bucket, {timestamp: value})
                            for metric_bucket in metric_buckets]
        metrics_controller.read = mock.Mock(return_value=metrics_response)
        extras = {
            'metricType': metrictype,
            'startTime': startTime,
            'endTime': endTime,
            'metrics_controller': metrics_controller
        }

        formatted_results = controller.get_metrics_by_domain(project_id,
                                                             domain_name,
                                                             regions,
                                                             **extras)

        self.assertEqual(formatted_results['domain'], domain_name)
        self.assertEqual(sorted(formatted_results[metrictype].keys()),
                         sorted(regions))
        for timestamp_counter in formatted_results[metrictype].values():
            self.assertEqual(timestamp_counter[0][timestamp], value)

    def test_get_provider_service_id(self):
        controller = services.ServiceController(self.driver)

        expected_id = []

        for service_domain in self.service_obj.domains:
            dp_obj = {'policy_name': service_domain.domain,
                      'protocol': service_domain.protocol,
                      'certificate': service_domain.certificate}
            expected_id.append(dp_obj)

        actual_id = controller.get_provider_service_id(self.service_obj)

        self.assertEqual(json.dumps(expected_id), actual_id)

    def test_get(self):
        controller = services.ServiceController(self.driver)
        self.assertIsNone(controller.get('service_name'))

    def test_current_customer(self):
        controller = services.ServiceController(self.driver)
        self.assertIsNone(controller.current_customer)

    @ddt.file_data('caching_rules.json')
    def test_reorder_rules(self, caching_rules_json):
        res = self.controller.reorder_rules(caching_rules_json['input'])
        self.assertEqual(res, caching_rules_json['output']['rules'])
