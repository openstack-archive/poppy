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

from cafe.engine.models import data_interfaces


class PoppyConfig(data_interfaces.ConfigSectionInterface):
    """Defines the config values for poppy."""
    SECTION_NAME = 'poppy'

    @property
    def base_url(self):
        """poppy endpoint."""
        return self.get('base_url')

    @property
    def flavor(self):
        """poppy flavor definitions."""
        return json.loads(self.get('flavor'))


class TestConfig(data_interfaces.ConfigSectionInterface):
    """Defines the config values specific to test execution."""
    SECTION_NAME = 'test_configuration'

    @property
    def provider_validation(self):
        """Boolean value indicating if tests verify provider side details."""
        return self.get_boolean('provider_validation')

    @property
    def run_operator_tests(self):
        """Boolean flag indicating if tests for operator apis should be run."""
        return self.get_boolean('run_operator_tests')

    @property
    def status_check_retry_interval(self):
        """Int value to set retry intervals for status check."""
        return int(self.get('status_check_retry_interval'))

    @property
    def status_check_retry_timeout(self):
        """Int value to set timeout for status check."""
        return int(self.get('status_check_retry_timeout'))

    @property
    def generate_flavors(self):
        """Boolean value to create unique flavors in tests."""
        return self.get_boolean('generate_flavors')

    @property
    def default_flavor(self):
        """String value to set the default flavor to use in tests."""
        return self.get('default_flavor')

    @property
    def generated_provider(self):
        """String value to set the provider to use with generated flavor."""
        return self.get('generated_provider')

    @property
    def project_id_in_url(self):
        """Flag to indicate if project_id should be present in the url."""
        return self.get_boolean('project_id_in_url')

    @property
    def run_ssl_tests(self):
        """Flag to indicate if positive tests for SSL cert should run."""
        return self.get_boolean('run_ssl_tests')

    @property
    def run_hypothesis_tests(self):
        """Flag to indicate if the hypothesis tests should run."""
        return self.get_boolean('run_hypothesis_tests')

    @property
    def cassandra_consistency_wait_time(self):
        """Int value in seconds to wait for cassandra consistency."""
        return int(self.get('cassandra_consistency_wait_time'))


class DNSConfig(data_interfaces.ConfigSectionInterface):
    """Defines the values for DNS configuration."""
    SECTION_NAME = 'dns'

    @property
    def dns_username(self):
        """The user name for the Cloud DNS service"""
        return self.get('dns_username')

    @property
    def dns_api_key(self):
        """The API Key for the Cloud DNS service"""
        return self.get('dns_api_key')

    @property
    def dns_url_suffix(self):
        """The url for customers to CNAME to."""
        return self.get('dns_url_suffix')

    @property
    def shared_ssl_num_shards(self):
        """The number of shared ssl shards."""
        return int(self.get('shared_ssl_num_shards'))


class AuthConfig(data_interfaces.ConfigSectionInterface):
    """Defines the auth config values."""
    SECTION_NAME = 'auth'

    @property
    def auth_enabled(self):
        """Auth On/Off."""
        return self.get_boolean('auth_enabled')

    @property
    def base_url(self):
        """Auth endpoint."""
        return self.get('base_url')

    @property
    def user_name(self):
        """The name of the user, if applicable."""
        return self.get('user_name')

    @property
    def api_key(self):
        """The user's api key, if applicable."""
        return self.get_raw('api_key')

    @property
    def password(self):
        """The user's password, if applicable."""
        return self.get_raw('password')

    @property
    def multi_user(self):
        """Flag to indicate if the tests need multiple accounts."""
        return self.get_boolean('multi_user')

    @property
    def alt_user_name(self):
        """The name of the alternate user, if applicable."""
        return self.get('alt_user_name')

    @property
    def alt_api_key(self):
        """The alternate user's api key, if applicable."""
        return self.get_raw('alt_api_key')

    @property
    def service_limit_user_name(self):
        """The name of the service limit user, if applicable."""
        return self.get('service_limit_user_name')

    @property
    def service_limit_api_key(self):
        """The service limit user's api key, if applicable."""
        return self.get_raw('service_limit_api_key')

    @property
    def operator_user_name(self):
        """The name of the user, if applicable."""
        return self.get('operator_user_name')

    @property
    def operator_api_key(self):
        """The user's api key, if applicable."""
        return self.get_raw('operator_api_key')


class AkamaiConfig(data_interfaces.ConfigSectionInterface):
    """Defines the Akamai config values."""
    SECTION_NAME = 'provider_akamai'

    @property
    def access_url_suffix(self):
        """The access URL suffix for Akamai"""
        return self.get('access_url_suffix')

    @property
    def san_certs(self):
        """A list of SAN certificates from Akamai"""
        return self.get('san_certs')

    @property
    def san_certs_name_positive(self):
        """SAN cert name used to test get san info (positive case)"""
        return self.get('get_san_certs_name_positive')

    @property
    def san_certs_name_negative(self):
        """SAN cert name used to test get san info (positive case)"""
        return self.get('get_san_certs_name_negative')


class FastlyConfig(data_interfaces.ConfigSectionInterface):
    """Defines the fastly config values."""
    SECTION_NAME = 'fastly'

    @property
    def api_key(self):
        """Fastly API Key."""
        return self.get('api_key')

    @property
    def email(self):
        """Email id associated with Fastly account."""
        return self.get('email')

    @property
    def password(self):
        """Fastly password."""
        return self.get('password')
