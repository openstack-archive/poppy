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

from poppy.dns.rackspace import driver
from poppy.model.helpers import provider_details
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


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('pyrax.set_credentials')
    @mock.patch.object(driver, 'RACKSPACE_OPTIONS', new=RACKSPACE_OPTIONS)
    def setUp(self, mock_set_credentials):
        super(TestServices, self).setUp()
        provider = driver.DNSProvider(self.conf)
        self.controller = provider.services_controller

    def test_create_with_provider_failure(self):
        responders = [{
            'Fastly':
                {'error_detail': 'Error in create',
                 'error': 'failed to create service'}}]
        self.controller.create(responders)

    def test_create(self):
        responders = [{
            'Fastly': {
                'id': u'4PRhL3lHlZhrXr1mJUt24M',
                'links': [
                    {
                        'domain': u'blog.mocksite4.com',
                        'href': u'blog.mocksite4.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    },
                    {
                        'domain': u'test.mocksite4.com',
                        'href': u'test.mocksite4.com.global.prod.fastly.net',
                        'rel': 'access_url'
                    }
                ]}
            }]
        self.controller.create(responders)

    def test_delete(self):
        fastly_details = provider_details.ProviderDetail(
            provider_service_id=u'6O0Ic4DyV7iFflikcOxPyA',
            access_urls=[
                {
                    u'provider_url':
                        u'blog.mocksite45.com.global.prod.fastly.net',
                    u'domain': u'blog.mocksite45.com',
                    u'operator_url': u'blog.mocksite45.com.cdn197.myaltcdn.com'
                },
                {
                    u'provider_url':
                        u'test.mocksite45.com.global.prod.fastly.net',
                    u'domain': u'test.mocksite45.com',
                    u'operator_url': u'test.mocksite45.com.cdn197.myaltcdn.com'
                }],
            status=u'delete_in_progress',
            name=None,
            error_info=None)
        details = {u'Fastly': fastly_details}
        self.controller.delete(details)
