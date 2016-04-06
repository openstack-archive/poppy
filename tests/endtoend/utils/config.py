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

from cafe.engine.models import data_interfaces


class PoppyConfig(data_interfaces.ConfigSectionInterface):
    """Defines the config values for poppy."""
    SECTION_NAME = 'poppy'

    @property
    def base_url(self):
        """poppy endpoint."""
        return self.get('base_url')

    @property
    def project_id_in_url(self):
        """flag to indicate if project id should be present in url."""
        return self.get_boolean('project_id_in_url')

    @property
    def flavor(self):
        """poppy flavor to use in create service call."""
        return self.get('flavor')

    @property
    def status_check_retry_interval(self):
        """Int value to set retry intervals for status check."""
        return int(self.get('status_check_retry_interval'))

    @property
    def status_check_retry_timeout(self):
        """Int value to set timeout for status check."""
        return int(self.get('status_check_retry_timeout'))


class TestConfig(data_interfaces.ConfigSectionInterface):
    """Defines the config values specific to test execution."""
    SECTION_NAME = 'test_configuration'

    @property
    def default_origin(self):
        """Default origin for all tests

        Use the test site below.
        https://github.com/stackforge/poppy/tree/master/docker/e2e_test.
        """
        return self.get('default_origin')

    @property
    def alternate_origin(self):
        """Alternate origin with any type of content."""
        return self.get('alternate_origin')

    @property
    def ssl_origin(self):
        """IP address for ssl origin."""
        return self.get('ssl_origin')

    @property
    def run_ssl_tests(self):
        """Flag to indicate if ssl tests should be run."""
        return self.get_boolean('run_ssl_tests')

    @property
    def webpagetest_enabled(self):
        """Flag to indicate if webpagetest tests should be run."""
        return self.get_boolean('webpagetest_enabled')

    @property
    def referree_origin(self):
        """The origin to use during referrer restriction tests."""
        return self.get('referree_origin')

    @property
    def referrer_request_url(self):
        """The url that referrer restrictions are applied to"""
        return self.get('referrer_request_url')


class AuthConfig(data_interfaces.ConfigSectionInterface):
    """Defines the auth config values."""
    SECTION_NAME = 'auth'

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


class WebPageTestConfig(data_interfaces.ConfigSectionInterface):
    """Defines the webpage test config values."""
    SECTION_NAME = 'webpagetest'

    @property
    def base_url(self):
        """Auth endpoint."""
        return self.get('base_url')

    @property
    def api_key(self):
        """The user's api key."""
        return self.get_raw('api_key')

    @property
    def test_locations(self):
        """Locations from which to test page load."""
        return self.get('test_locations').split(',')


class DNSConfig(data_interfaces.ConfigSectionInterface):
    """Defines the DNS config values."""
    SECTION_NAME = 'dns'

    @property
    def email(self):
        """Email address."""
        return self.get('email')

    @property
    def test_domain(self):
        """The Domain to use in tests."""
        return self.get('test_domain')

    @property
    def retry_interval(self):
        """Int value to set retry interval for dns polling."""
        return int(self.get('retry_interval'))

    @property
    def retry_timeout(self):
        """Int value to set timeout for dns polling."""
        return int(self.get('retry_timeout'))

    @property
    def dns_api_timeout(self):
        """The timeout when waiting for Cloud DNS API requests to complete"""
        return int(self.get('dns_api_timeout'))

    @property
    def authoritative_nameserver(self):
        """The authoritative nameserver to query, must be an ip address."""
        return self.get('authoritative_nameserver')

    @property
    def cname_propagation_sleep(self):
        """Sleep to wait for caching nameservers to pick up a changes."""
        return int(self.get('cname_propagation_sleep'))

    @property
    def cdn_provider_dns_sleep(self):
        """Sleep to avoid fetching an access_url too soon."""
        return int(self.get('cdn_provider_dns_sleep'))


class CachingConfig(data_interfaces.ConfigSectionInterface):
    """Defines the config values for caching tests."""
    SECTION_NAME = 'caching'

    @property
    def endpoint(self):
        """Path to cacheable content."""
        return self.get('cache_path')

    @property
    def jpg_endpoint(self):
        """Path to jpg content."""
        return self.get('jpg_path')

    @property
    def jpg_ttl(self):
        """TTL for jpg content."""
        return int(self.get('jpg_ttl'))

    @property
    def txt_endpoint(self):
        """Path to txt content."""
        return self.get('txt_path')

    @property
    def txt_ttl(self):
        """TTL for txt content."""
        return int(self.get('txt_ttl'))

    @property
    def zip_endpoint(self):
        """Path to zip content."""
        return self.get('zip_path')

    @property
    def zip_ttl(self):
        """TTL for zip content."""
        return int(self.get('zip_ttl'))


class MultipleOriginConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for testing multiple origins."""
    SECTION_NAME = 'multiple_origin'

    @property
    def second_origin(self):
        return self.get('second_origin')

    @property
    def request_url(self):
        """The uri which should be directed to second origin."""
        return self.get('request_url')


class HostHeaderConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for testing multiple origins."""
    SECTION_NAME = 'host_header'

    @property
    def endpoint(self):
        return self.get('endpoint')


class PurgeConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for purge tests."""
    SECTION_NAME = 'purge'

    @property
    def purge_path(self):
        return self.get('purge_path')

    @property
    def cache_ttl(self):
        return int(self.get('cache_ttl'))

    @property
    def purge_wait_time(self):
        return int(self.get('purge_wait_time'))


class OriginHeaderConfig(data_interfaces.ConfigSectionInterface):
    """Defines the origin header config values."""
    SECTION_NAME = 'origin_headers'

    @property
    def expires_ttl(self):
        """TTL for expires header."""
        return int(self.get('expires_ttl'))

    @property
    def expires_path(self):
        """expires endpoint."""
        return self.get('expires_path')

    @property
    def cache_control_ttl(self):
        """TTL for cache control header."""
        return int(self.get('cache_control_ttl'))

    @property
    def cache_control_path(self):
        """cache_control_path endpoint."""
        return self.get('cache_control_path')

    @property
    def service_ttl(self):
        """TTL for Service."""
        return int(self.get('service_ttl'))

    @property
    def expires_and_cache_control_path(self):
        """expires_and_cache_control_path endpoint."""
        return self.get('expires_and_cache_control_path')


class GeoRestrictionsConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for testing geo restrictions."""
    SECTION_NAME = 'geo_restrictions'

    @property
    def test_geo(self):
        return self.get('test_geo')

    @property
    def image_path(self):
        """The uri at which the images_origin serves an image."""
        return self.get('image_path')
