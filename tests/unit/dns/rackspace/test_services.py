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

import uuid

import ddt
import mock
from oslo_config import cfg
import pyrax.exceptions as exc

from poppy.dns.rackspace import driver
from poppy.model.helpers import domain
from poppy.model import service
from tests.unit import base

RACKSPACE_OPTIONS = [
    cfg.StrOpt('username', default='',
               help='Keystone Username'),
    cfg.StrOpt('api_key', default='',
               help='Keystone API Key'),
    cfg.BoolOpt('sharding_enabled', default=True,
                help='Enable Sharding?'),
    cfg.IntOpt('num_shards', default=500, help='Number of Shards to use'),
    cfg.StrOpt('shard_prefix', default='cdn',
               help='The shard prefix to use'),
    cfg.StrOpt('url', default='mycdn.com',
               help='The url for customers to CNAME to'),
    cfg.StrOpt('email', help='The email to be provided to Rackspace DNS for'
               'creating subdomains'),
    cfg.StrOpt('auth_endpoint', default='',
               help='Authentication end point for DNS'),
    cfg.IntOpt('timeout', default=30, help='DNS response timeout'),
    cfg.IntOpt('delay', default=1, help='DNS retry delay'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'


@ddt.ddt
class TestServicesCreate(base.TestCase):

    def setUp(self):
        super(TestServicesCreate, self).setUp()

        pyrax_cloud_dns_patcher = mock.patch('pyrax.cloud_dns')
        pyrax_cloud_dns_patcher.start()
        self.addCleanup(pyrax_cloud_dns_patcher.stop)

        pyrax_set_credentials_patcher = mock.patch('pyrax.set_credentials')
        pyrax_set_credentials_patcher.start()
        self.addCleanup(pyrax_set_credentials_patcher.stop)

        pyrax_set_setting_patcher = mock.patch('pyrax.set_setting')
        pyrax_set_setting_patcher.start()
        self.addCleanup(pyrax_set_setting_patcher.stop)

        rs_options_patcher = mock.patch.object(
            driver,
            'RACKSPACE_OPTIONS',
            new=RACKSPACE_OPTIONS
        )
        rs_options_patcher.start()
        self.addCleanup(rs_options_patcher.stop)

        provider = driver.DNSProvider(self.conf)
        self.client = mock.Mock()
        self.controller = provider.services_controller
        self.controller.client = self.client

    def test_create_with_no_links(self):
        responders = [{
            'Akamai': {
                'id': str(uuid.uuid4()),
                'links': []
            },
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': []
            }
        }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        dns_details = self.controller.create(responders)

        for responder in responders:
            for provider_name in responder:
                self.assertEqual([], dns_details[provider_name]['access_urls'])

    def test_create_with_provider_error(self):

        responders = [{
            'Akamai': {
                'error': 'Create service failed with Akamai',
                'error_detail': 'Error details'
                },
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.mocksite.com',
                        'href': u'blog.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.mocksite.com',
                        'href': u'test.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        dns_details = self.controller.create(responders)

        for responder in responders:
            for provider_name in responder:
                self.assertIsNotNone(dns_details[provider_name]['error'])
                self.assertIsNotNone(
                    dns_details[provider_name]['error_detail'])

    def test_create_with_subdomain_not_found_exception(self):
        domain_names = [u'blog.mocksite.com', u'test.mocksite.com']
        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.mocksite.com',
                        'href': u'blog.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.mocksite.com',
                        'href': u'test.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        self.client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        dns_details = self.controller.create(responders)

        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_name in domain_names:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_name])

    def test_create_with_generic_exception(self):
        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.mocksite.com',
                        'href': u'blog.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.mocksite.com',
                        'href': u'test.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        self.client.find = mock.Mock(return_value=subdomain)
        dns_details = self.controller.create(responders)

        for responder in responders:
            for provider_name in responder:
                self.assertIsNotNone(dns_details[provider_name]['error'])
                self.assertIsNotNone(
                    dns_details[provider_name]['error_detail'])

    def test_create(self):
        domain_names = [u'blog.mocksite.com', u'test.mocksite.com']
        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.mocksite.com',
                        'href': u'blog.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.mocksite.com',
                        'href': u'test.mocksite.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'href': 'https://cloudfiles.rackspace/CONTAINER/OBJ',
                        'rel': 'log_delivery'
                    },
                    {
                        'domain': u'shared.mocksite.com',
                        'href': u'test.mocksite.com.global.prod.fastly.net',
                        'certificate': 'shared',
                        'rel': 'access_url'
                    },
                ]}
            }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        dns_details = self.controller.create(responders)

        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_name in domain_names:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_name])


@ddt.ddt
class TestServicesDelete(base.TestCase):

    def setUp(self):
        super(TestServicesDelete, self).setUp()

        pyrax_cloud_dns_patcher = mock.patch('pyrax.cloud_dns')
        pyrax_cloud_dns_patcher.start()
        self.addCleanup(pyrax_cloud_dns_patcher.stop)

        pyrax_set_credentials_patcher = mock.patch('pyrax.set_credentials')
        pyrax_set_credentials_patcher.start()
        self.addCleanup(pyrax_set_credentials_patcher.stop)

        pyrax_set_setting_patcher = mock.patch('pyrax.set_setting')
        pyrax_set_setting_patcher.start()
        self.addCleanup(pyrax_set_setting_patcher.stop)

        rs_options_patcher = mock.patch.object(
            driver,
            'RACKSPACE_OPTIONS',
            new=RACKSPACE_OPTIONS
        )
        rs_options_patcher.start()
        self.addCleanup(rs_options_patcher.stop)

        provider = driver.DNSProvider(self.conf)
        self.client = mock.Mock()
        self.controller = provider.services_controller
        self.controller.client = self.client

    def test_delete_with_exception_subdomain_not_found(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        self.client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertIsNotNone(dns_responder[provider_name]['error'])
            self.assertIsNotNone(dns_responder[provider_name]['error_detail'])
            self.assertIsNotNone(
                dns_responder[provider_name]['error_class']
            )

    def test_delete_with_generic_exception(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        self.client.search_records = mock.Mock(
            side_effect=Exception('Generic exception'))

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertIsNotNone(dns_responder[provider_name]['error'])
            self.assertIsNotNone(dns_responder[provider_name]['error_detail'])
            self.assertIsNotNone(
                dns_responder[provider_name]['error_class']
            )

    def test_delete_no_records_found(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        self.client.search_records = mock.Mock(return_value=[])

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertEqual({}, dns_responder[provider_name])

    def test_delete_with_more_than_one_record_found(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            },
            {
                u'provider_url': u'test.com.global.fastly.net',
                u'domain': u'mocksite.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        records = [mock.Mock(), mock.Mock()]
        self.client.search_records = mock.Mock(return_value=records)

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertIsNotNone(dns_responder[provider_name]['error'])
            self.assertIsNotNone(dns_responder[provider_name]['error_detail'])

    def test_delete_with_delete_exception(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        record = mock.Mock()
        record.delete = mock.Mock(
            side_effect=exc.NotFound('Generic exception'))
        self.client.search_records = mock.Mock(return_value=[record])

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertIsNotNone(dns_responder[provider_name]['error'])
            self.assertIsNotNone(dns_responder[provider_name]['error_detail'])
            self.assertIsNotNone(
                dns_responder[provider_name]['error_class']
            )

    def test_delete(self):
        akamai_access_urls = [
            {
                u'provider_url': u'mycdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.com.cdn80.mycdn.com'
            }
        ]

        fastly_access_urls = [
            {
                u'provider_url': u'mocksite.com.global.fastly.net',
                u'domain': u'mocksite.com',
                u'operator_url': u'mocksite.cdn80.mycdn.com'
            }
        ]

        akamai_details = mock.Mock()
        akamai_details.access_urls = akamai_access_urls
        fastly_details = mock.Mock()
        fastly_details.access_urls = fastly_access_urls
        provider_details = {
            'Akamai': akamai_details,
            'Fastly': fastly_details
        }

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)
        record = mock.Mock()
        self.client.search_records = mock.Mock(return_value=[record])

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertEqual({}, dns_responder[provider_name])


@ddt.ddt
class TestServicesUpdate(base.TestCase):

    def setUp(self):
        super(TestServicesUpdate, self).setUp()

        pyrax_cloud_dns_patcher = mock.patch('pyrax.cloud_dns')
        pyrax_cloud_dns_patcher.start()
        self.addCleanup(pyrax_cloud_dns_patcher.stop)

        pyrax_set_credentials_patcher = mock.patch('pyrax.set_credentials')
        pyrax_set_credentials_patcher.start()
        self.addCleanup(pyrax_set_credentials_patcher.stop)

        pyrax_set_setting_patcher = mock.patch('pyrax.set_setting')
        pyrax_set_setting_patcher.start()
        self.addCleanup(pyrax_set_setting_patcher.stop)

        rs_options_patcher = mock.patch.object(
            driver,
            'RACKSPACE_OPTIONS',
            new=RACKSPACE_OPTIONS
        )
        rs_options_patcher.start()
        self.addCleanup(rs_options_patcher.stop)

        self.client = mock.Mock()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller
        self.controller.client = self.client

        self.domains_old = [domain.Domain('test.domain.com'),
                            domain.Domain('blog.domain.com')]
        self.origins_old = []

        fastly_access_urls_old = [
            {
                u'provider_url': u'test.domain.com.global.prod.fastly.net',
                u'domain': u'test.domain.com',
                u'operator_url': u'test.domain.com.cdn80.mycdn.com'
            },
            {
                u'provider_url': u'blog.domain.com.global.prod.fastly.net',
                u'domain': u'blog.domain.com',
                u'operator_url': u'blog.domain.com.cdn80.mycdn.com'
            }
        ]

        fastly_provider_details_old = mock.Mock()
        fastly_provider_details_old.access_urls = fastly_access_urls_old

        provider_details_old = {
            'Fastly': fastly_provider_details_old
        }

        self.service_old = service.Service(service_id=uuid.uuid4(),
                                           name='myservice',
                                           domains=self.domains_old,
                                           origins=self.origins_old,
                                           flavor_id='standard')
        self.service_old.provider_details = provider_details_old

    def test_update_add_domains_with_dns_exception(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(
            side_effect=Exception('DNS Exception'))
        self.controller.client = client

        domains_new = [domain.Domain('test.domain.com'),
                       domain.Domain('blog.domain.com'),
                       domain.Domain('pictures.domain.com')]
        service_updates = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=domains_new,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'blog.domain.com',
                        'href': u'blog.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'pictures.domain.com',
                        'href': u'pictures.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_updates,
                                             responders)
        for responder in responders:
            for provider_name in responder:
                    self.assertIsNotNone(dns_details[provider_name]['error'])
                    self.assertIsNotNone(
                        dns_details[provider_name]['error_detail'])
                    self.assertIsNotNone(
                        dns_details[provider_name]['error_class']
                    )

    def test_update_add_domains_with_no_domains_in_update(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        self.controller.client = client

        service_updates = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=[],
            origins=[],
            flavor_id='standard'
        )

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'blog.domain.com',
                        'href': u'blog.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'pictures.domain.com',
                        'href': u'pictures.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(
            self.service_old,
            service_updates,
            responders
        )

        access_urls_map = {}
        for provider_name in self.service_old.provider_details:
            provider_detail = self.service_old.provider_details[provider_name]
            access_urls = provider_detail.access_urls
            access_urls_map[provider_name] = {'access_urls': access_urls}

        self.assertEqual(access_urls_map, dns_details)

    def test_update_remove_domains_provider_error(self):
        domains_new = [domain.Domain('test.domain.com'),
                       domain.Domain('blog.domain.com'),
                       domain.Domain('pictures.domain.com')]
        service_new = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=domains_new,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'error': 'Create service failed'
                }
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_new,
                                             responders)
        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_old in self.domains_old:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_old.domain])

    def test_update_remove_domains_with_subdomain_not_found_exception(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        records = [mock.Mock(), mock.Mock()]
        client.search_records = mock.Mock(return_value=records)
        self.controller.client = client

        domains_new = [domain.Domain('test.domain.com'),
                       domain.Domain('blog.domain.com')]
        service_updates = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=domains_new,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.domain.com',
                        'href': u'blog.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_updates,
                                             responders)
        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_new in domains_new:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_new.domain])

    def test_update_remove_domains(self):
        domains_new = [domain.Domain('test.domain.com')]
        service_updates = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=domains_new,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_updates,
                                             responders)
        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_new in domains_new:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_new.domain])

    def test_update_same_domains(self):
        service_updates = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=self.domains_old,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'blog.domain.com',
                        'href': u'blog.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_updates,
                                             responders)
        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_old in self.domains_old:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_old.domain])

    def test_update_add_domains(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        self.client.find = mock.Mock(return_value=subdomain)

        domains_new = [domain.Domain('test.domain.com'),
                       domain.Domain('blog.domain.com'),
                       domain.Domain('pictures.domain.com')]

        service_new = service.Service(
            service_id=self.service_old.service_id,
            name='myservice',
            domains=domains_new,
            origins=[],
            flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': str(uuid.uuid4()),
                'links': [
                    {
                        'domain': u'test.domain.com',
                        'href': u'test.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'blog.domain.com',
                        'href': u'blog.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'pictures.domain.com',
                        'href': u'pictures.domain.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]

        dns_details = self.controller.update(self.service_old,
                                             service_new,
                                             responders)
        access_urls_map = {}
        for provider_name in dns_details:
            access_urls_map[provider_name] = {}
            access_urls_list = dns_details[provider_name]['access_urls']
            for access_urls in access_urls_list:
                access_urls_map[provider_name][access_urls['domain']] = (
                    access_urls['operator_url'])

        for responder in responders:
            for provider_name in responder:
                for domain_new in domains_new:
                    self.assertIsNotNone(
                        access_urls_map[provider_name][domain_new.domain])

    def test_gather_cname_links_positive(self):
        cname_links = self.controller.gather_cname_links(self.service_old)
        # TODO(isaacm): Add assertions on the returned object
        self.assertIsNotNone(cname_links)

    def test_enable_positive(self):
        responder_enable = self.controller.enable(self.service_old)
        # TODO(isaacm): Add assertions on the returned object
        self.assertIsNotNone(responder_enable)

    def test_disable_positive(self):
        responder_disable = self.controller.disable(self.service_old)
        # TODO(isaacm): Add assertions on the returned object
        self.assertIsNotNone(responder_disable)
