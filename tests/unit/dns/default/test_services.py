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

from poppy.dns.default import driver
from poppy.model.helpers import domain
from poppy.model import service
from tests.unit import base


@ddt.ddt
class TestServicesCreate(base.TestCase):

    def setUp(self):
        super(TestServicesCreate, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

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
        dns_details = self.controller.create(responders)

        # returned default dns details should not contain any errors
        for provider_name in dns_details:
            self.assertNotIn('error', dns_details[provider_name])
            self.assertNotIn('error_detail', dns_details[provider_name])

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
                    }
                ]}
            }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
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
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

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

        dns_responder = self.controller.delete(provider_details)
        for provider_name in provider_details:
            self.assertEqual({}, dns_responder[provider_name])


@ddt.ddt
class TestServicesUpdate(base.TestCase):

    def setUp(self):
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
                u'operator_url': u'test.domain.com.cdn80.mycdn.com'
            },
            {
                u'provider_url': u'blog.domain.com.global.prod.fastly.net',
                u'domain': u'blog.domain.com',
                u'operator_url': u'blog.domain.com.cdn80.mycdn.com'
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
        # dns_details should be empty because the only responder available
        # had an error an gets filtered
        self.assertEqual({}, dns_details)

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

        dns_details = self.controller.update(
            self.service_old,
            service_new,
            responders
        )
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
