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
from oslo.config import cfg
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
    cfg.StrOpt('url', default='rackcdn.com',
               help='The url for customers to CNAME to'),
    cfg.StrOpt('email', help='The email to be provided to Rackspace DNS for'
               'creating subdomains'),
    cfg.StrOpt('auth_endpoint', default='',
               help='Authentication end point for DNS'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'


@ddt.ddt
class TestServicesCreate(base.TestCase):

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def setUp(self, mock_set_credentials):
        super(TestServicesCreate, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.client = mock.Mock()
        self.controller = provider.services_controller
        self.controller.client = self.client

    def test_create_with_no_links(self):
        responders = [{
            'Akamai': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
                'links': []
            },
            'Fastly': {
                'id': u'6HGJjRhdsDjDSkfGSjdsKD',
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
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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
class TestServicesUpdate(base.TestCase):

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def setUp(self, mock_set_credentials):
        super(TestServicesUpdate, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

        self.domains_old = [domain.Domain('test.domain.com'),
                            domain.Domain('blog.domain.com')]
        self.origins_old = []

        fastly_access_urls_old = [
            {
                u'provider_url': u'test.domain.com.global.prod.fastly.net',
                u'domain': u'test.domain.com',
                u'operator_url': u'test.domain.com.cdn80.myaltcdn.com'
            },
            {
                u'provider_url': u'test.domain.com.global.prod.fastly.net',
                u'domain': u'test.domain.com',
                u'operator_url': u'test.domain.com.cdn80.myaltcdn.com'
            }]

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

    def test_update_add_domains_provider_error(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        # records = [mock.Mock(), mock.Mock()]
        # client.search_records = mock.Mock(return_value=records)
        self.controller.client = client

        domains_new = [domain.Domain('www.domain1.com'),
                       domain.Domain('www.domain2.com'),
                       domain.Domain('www.domain3.com')]
        service_updates = service.Service(service_id=uuid.uuid4(),
                                          name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
                'error': 'Create service failed'
            }
        }]

        self.controller.update(self.service_old,
                               service_updates,
                               responders)
