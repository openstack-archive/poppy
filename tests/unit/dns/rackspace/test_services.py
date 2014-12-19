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
    cfg.IntOpt('num_shards', default=10, help='Number of Shards to use'),
    cfg.StrOpt('shard_prefix', default='cdn',
               help='The shard prefix to use'),
    cfg.StrOpt('url', default='',
               help='The url for customers to CNAME to'),
    cfg.StrOpt('email', help='The email to be provided to Rackspace DNS for'
               'creating subdomains'),
    cfg.StrOpt('auth_endpoint', default='',
               help='Authentication end point for DNS'),
]

RACKSPACE_GROUP = 'drivers:dns:rackspace'

"""
dns_links = {
    u'blog.mocksite.com.global.prod.fastly.net':
        u'blog.mocksite.com.altcdn.com',
    u'test.mocksite.com.global.prod.fastly.net':
        u'test.mocksite.com.altcdn.com',
}
"""
"""
akamai_access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                    u'domain': u'www.mocksite.com',
                    u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]
akamai_provider_details = mock.Mock()
akamai_provider_details.access_urls = akamai_access_urls
old_provider_details = {
    'Akamai': akamai_provider_details
}

self.service_old = mock.Mock()
self.service_old.provider_details = old_provider_details
self.service_updates = mock.Mock()



dns_links = {
    u'blog.mocksite.com.global.prod.fastly.net':
        u'blog.mocksite.com.altcdn.com',
    u'test.mocksite.com.global.prod.fastly.net':
        u'test.mocksite.com.altcdn.com',
}

access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                u'domain': u'mocksite',
                u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

akamai_details = mock.Mock()
akamai_details.access_urls = access_urls
provider_details = {'Akamai': akamai_details}
"""


@ddt.ddt
class TestServicesCreate(base.TestCase):

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def setUp(self, mock_set_credentials):
        super(TestServicesCreate, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

    def test_create_with_no_links(self):
        responders = [{
            'Akamai': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
                'links': []
            },
            'Fastly': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
                'error': 'Create service failed with Fastly',
                'links': []
            }
        }]

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        self.controller.client = client
        self.controller.create(responders)

    def test_create_with_provider_error(self):

        responders = [{
            'Akamai': {
                'error': 'Create service failed with Akamai'
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
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        self.controller.client = client
        self.controller.create(responders)

    def test_create_with_subdomain_not_found_exception(self):

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

        client = mock.Mock()
        client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        self.controller.client = client
        self.controller.create(responders)

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
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        self.controller.client = client
        self.controller.create(responders)

    def test_create(self):

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
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        self.controller.client = client
        self.controller.create(responders)


@ddt.ddt
class TestServicesDelete(base.TestCase):

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def setUp(self, mock_set_credentials):
        super(TestServicesDelete, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

    def test_delete_with_exception_subdomain_not_found(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        client = mock.Mock()
        client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        self.controller.client = client
        self.controller.delete(provider_details)

    def test_delete_with_generic_exception(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        client.search_records = mock.Mock(
            side_effect=Exception('Generic exception'))
        self.controller.client = client
        self.controller.delete(provider_details)

    def test_delete_no_records_found(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        client.search_records = mock.Mock(return_value=[])
        self.controller.client = client
        self.controller.delete(provider_details)

    def test_delete_with_more_than_one_record_found(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        records = [mock.Mock(), mock.Mock()]
        client.search_records = mock.Mock(return_value=records)
        self.controller.client = client
        self.controller.delete(provider_details)

    def test_delete_with_delete_exception(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        record = mock.Mock()
        record.delete = mock.Mock(
            side_effect=exc.NotFound('Generic exception'))
        client.search_records = mock.Mock(return_value=[record])
        self.controller.client = client
        self.controller.delete(provider_details)

    def test_delete(self):
        access_urls = [{u'provider_url': u'altcdn.com.v2.mdc.edgesuite.net',
                        u'domain': u'mocksite',
                        u'operator_url': u'mocksite.cdn80.myaltcdn.com'}]

        akamai_details = mock.Mock()
        akamai_details.access_urls = access_urls
        provider_details = {'Akamai': akamai_details}

        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        record = mock.Mock()
        client.search_records = mock.Mock(return_value=[record])
        self.controller.client = client
        self.controller.delete(provider_details)


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

        self.service_old = service.Service(name='myservice',
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

        domains_new = [domain.Domain('www.domain1.com'),
                       domain.Domain('www.domain2.com'),
                       domain.Domain('www.domain3.com')]
        service_updates = service.Service(name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)

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
        service_updates = service.Service(name='myservice',
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

    def test_update_add_domains(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        # records = [mock.Mock(), mock.Mock()]
        # client.search_records = mock.Mock(return_value=records)
        self.controller.client = client

        domains_new = [domain.Domain('test.domain.com'),
                       domain.Domain('blog.domain.com'),
                       domain.Domain('pictures.domain.com')]
        service_updates = service.Service(name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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
        self.controller.update(self.service_old,
                               service_updates,
                               responders)

    def test_update_remove_domains_provider_error(self):
        domains_new = [domain.Domain('www.domain1.com')]
        service_updates = service.Service(name='myservice',
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

    def test_update_remove_domains_with_multiple_dns_records(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(return_value=subdomain)
        records = [mock.Mock(), mock.Mock()]
        client.search_records = mock.Mock(return_value=records)
        self.controller.client = client

        domains_new = [domain.Domain('www.domain1.com'),
                       domain.Domain('www.domain2.com'),
                       domain.Domain('www.domain3.com')]
        service_updates = service.Service(name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)

    def test_update_remove_domains_with_subdomain_not_found_exception(self):
        subdomain = mock.Mock()
        subdomain.add_records = mock.Mock()
        client = mock.Mock()
        client.find = mock.Mock(
            side_effect=exc.NotFound('Subdomain not found'))
        records = [mock.Mock(), mock.Mock()]
        client.search_records = mock.Mock(return_value=records)
        self.controller.client = client

        domains_new = [domain.Domain('www.domain1.com'),
                       domain.Domain('www.domain2.com'),
                       domain.Domain('www.domain3.com')]
        service_updates = service.Service(name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)

    def test_update_remove_domains(self):
        domains_new = [domain.Domain('test.domain.com')]
        service_updates = service.Service(name='myservice',
                                          domains=domains_new,
                                          origins=[],
                                          flavor_id='standard')

        responders = [{
            'Fastly': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)

    def test_update_no_added_or_removed_domains(self):
        service_updates = service.Service(name='myservice',
                                          domains=[],
                                          origins=[],
                                          flavor_id='standard')

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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)

    def test_update_same_domains(self):
        service_updates = service.Service(name='myservice',
                                          domains=self.domains_old,
                                          origins=[],
                                          flavor_id='standard')

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

        self.controller.update(self.service_old,
                               service_updates,
                               responders)
