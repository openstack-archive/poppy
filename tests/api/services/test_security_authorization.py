# coding= utf-8

# Copyright (c) 2015 Rackspace, Inc.
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
import uuid

from nose.plugins import attrib
from tests.api import providers
from tests.api.utils import config


@ddt.ddt
class TestAuthorizationService(providers.TestProviderBase):

    """Security Tests for authorization vulnerabilities

    These test cases cover authorization checks for service functions.
    They check whether it is possible to create/patch/list/delete services
    without valid tokens or no token at all. It also checks whether it is
    possible to create/patch/list/delete services for one user using another
    user's valid token. The supposed responses should be 401 errors.

    """

    def setUp(self):
        """Setup for the tests"""
        super(TestAuthorizationService, self).setUp()
        self.auth_config = config.AuthConfig()
        if self.auth_config.auth_enabled is False:
            self.skipTest(
                'Auth is currently disabled in configuration')

        self.service_url = ''
        self.service_name = str(uuid.uuid1())
        self.flavor_id = self.test_flavor

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_create_service_no_token(self, test_data):
        """Check creating a service without token."""

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        # create header without token
        headers = {"X-Auth-Token": ""}
        kwargs = {"headers": headers}
        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id,
                                          requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_create_service_other_user_token(self, test_data):
        """Check creating a service with another user's token."""

        # replace the token with another user's token
        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}
        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id,
                                          requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

    @attrib.attr('security')
    def test_authorization_list_services_other_user_token(self):
        """Check listing services with another user's token."""

        self.service_url = ''

        # replace the token with another user's token
        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}

        resp = self.client.list_services(requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    def test_authorization_list_service_no_token(self):
        """Check listing all services with no token."""

        self.service_url = ''

        # create header without token
        headers = {"X-Auth-Token": ""}
        kwargs = {"headers": headers}

        resp = self.client.list_services(requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_get_service_other_user_token(self, test_data):
        """Check getting one service with another user's token"""

        # replace the token with another user's token
        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.get_service(location=self.service_url,
                                       requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_get_service_no_token(self, test_data):
        """Check getting a service with no token."""

        # create header without token
        headers = {"X-Auth-Token": ""}
        kwargs = {"headers": headers}
        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.get_service(location=self.service_url,
                                       requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_delete_service_no_token(self, test_data):
        """Check deleting a service with no token."""

        # create header without token
        headers = {"X-Auth-Token": ""}
        kwargs = {"headers": headers}
        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        if self.service_url != '':
            resp = self.client.delete_service(location=self.service_url,
                                              requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_patch_service_another_token(self, test_data):
        """Check patching a service with another user's token."""

        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        test_patch_data = []
        domain_name = "api-test.replacemereplaceme%s.com" % str(uuid.uuid1())
        test_patch_data.append({"op": "add",
                                "path": "/domains/-",
                                "value": {"domain": "%s" % (domain_name)}})

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)

        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        if self.service_url != '':
            resp = self.client.patch_service(location=self.service_url,
                                             request_body=test_patch_data,
                                             requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_delete_service_other_user_token(self, test_data):
        """Check deleting one service with another user's token."""

        # replace the token with another user's token
        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        if self.service_url != '':
            resp = self.client.delete_service(location=self.service_url,
                                              requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_delete_service_invalid_token(self, test_data):
        """Check deleting a service with invalid token."""

        # create header without token
        headers = {"X-Auth-Token": "1" * 1000}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        if self.service_url != '':
            resp = self.client.delete_service(location=self.service_url,
                                              requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_get_service_invalid_token(self, test_data):
        """Check getting a service with invalid token."""

        # create header with invalid token
        headers = {"X-Auth-Token": "1" * 1000}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.get_service(location=self.service_url,
                                       requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    def test_authorization_list_service_invalid_token(self):
        """Check listing all services with invalid token."""

        self.service_url = ''

        # create header with invalid token
        headers = {"X-Auth-Token": "1" * 1000}
        kwargs = {"headers": headers}
        resp = self.client.list_services(requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_create_service_invalid_token(self, test_data):
        """Check creating a service with an invalid token."""

        # create header with invalid token
        headers = {"X-Auth-Token": "1" * 1000}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id,
                                          requestslib_kwargs=kwargs)
        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        self.assertTrue(resp.status_code == 401)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_patch_service_invalid_token(self, test_data):
        """Check patching a service with an invalid token."""

        # create header with invalid token
        headers = {"X-Auth-Token": "1" * 1000}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        test_patch_data = []
        domain_name = "api-test.replacemereplaceme%s.com" % str(uuid.uuid1())
        test_patch_data.append({"op": "add",
                                "path": "/domains/-",
                                "value": {"domain": "%s" % (domain_name)}})

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=test_patch_data,
                                         requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)
        self.client.delete_service(location=self.service_url)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_patch_service_other_user_token(self, test_data):
        """Check patching service with a valid token from another user."""
        # replace the token with another user's token
        headers = {"X-Auth-Token": self.alt_user_client.auth_token,
                   "X-Project-Id": self.client.project_id}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        test_patch_data = []
        domain_name = "api-test.replacemereplaceme%s.com" % str(uuid.uuid1())
        test_patch_data.append({"op": "add",
                                "path": "/domains/-",
                                "value": {"domain": "%s" % (domain_name)}})

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.patch_service(location=self.service_url,
                                         request_body=test_patch_data,
                                         requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)
        self.client.delete_service(location=self.service_url)

    @attrib.attr('security')
    @ddt.file_data('data_create_service_authorization.json')
    def test_authorization_patch_service_no_token(self, test_data):
        """Check patching a service with no token."""

        # create header without token
        headers = {"X-Auth-Token": ""}
        kwargs = {"headers": headers}

        domain_list = test_data['domain_list']
        for item in domain_list:
            item['domain'] = 'api-test.' + str(uuid.uuid1()) + '.com'
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor_id = self.flavor_id

        test_patch_data = []
        domain_name = "api-test.replacemereplaceme%s.com" % str(uuid.uuid1())
        test_patch_data.append({"op": "add",
                                "path": "/domains/-",
                                "value": {"domain": "%s" % (domain_name)}})

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavor_id=flavor_id)
        self.assertTrue(resp.status_code == 202)

        if 'location' in resp.headers:
            self.service_url = resp.headers['location']
        else:
            self.service_url = ''

        resp = self.client.get_service(location=self.service_url)
        self.assertTrue(resp.status_code == 200)
        resp = self.client.patch_service(location=self.service_url,
                                         request_body=test_patch_data,
                                         requestslib_kwargs=kwargs)
        self.assertTrue(resp.status_code == 401)

    def tearDown(self):
        if self.service_url != '':
            self.client.delete_service(location=self.service_url)

        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)

        super(TestAuthorizationService, self).tearDown()
