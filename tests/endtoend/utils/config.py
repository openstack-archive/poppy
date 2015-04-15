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
    def wordpress_origin(self):
        """IP address for wordpress origin."""
        return self.get('wordpress_origin')

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


class OrchestrationConfig(data_interfaces.ConfigSectionInterface):
    """Defines the Rackspace orchestration config values."""
    SECTION_NAME = 'orchestration'

    @property
    def base_url(self):
        """Orchestration base url."""
        return self.get('base_url')

    @property
    def yaml_path(self):
        """path to the heat yaml file."""
        return self.get('yaml_path')


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


class CacheRulesConfig(data_interfaces.ConfigSectionInterface):
    """Defines the cacherules config values."""
    SECTION_NAME = 'cacherules'

    @property
    def cache_rule1(self):
        """Cache Rule 1."""
        return self.get('cache_path_rule1')

    @property
    def ttl_rule1(self):
        """TTL for Cache Rule 1."""
        return int(self.get('ttl_rule1'))

    @property
    def cache_rule2(self):
        """Cache Rule 2."""
        return self.get('cache_path_rule2')

    @property
    def ttl_rule2(self):
        """TTL for Cache Rule 2."""
        return int(self.get('ttl_rule2'))

    @property
    def cache_rule3(self):
        """Cache Rule 3."""
        return self.get('cache_path_rule3')

    @property
    def ttl_rule3(self):
        """TTL for Cache Rule 3."""
        return int(self.get('ttl_rule3'))


class MultipleOriginConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for testing multiple origins."""
    SECTION_NAME = 'multiple_origin'

    @property
    def default_origin(self):
        return self.get('default_origin')

    @property
    def images_origin(self):
        return self.get('images_origin')

    @property
    def image_path(self):
        """The uri at which the images_origin serves an image."""
        return self.get('image_path')


class PurgeRulesConfig(data_interfaces.ConfigSectionInterface):
    """Configuration for purge wait time."""
    SECTION_NAME = 'purgetime'

    @property
    def purge_time(self):
        return int(self.get('purge_wait_time'))
