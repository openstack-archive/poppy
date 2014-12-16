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
    def project_id_in_url(self):
        """Flag to indicate if project_id should be present in the url."""
        return self.get_boolean('project_id_in_url')


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
    def tenant_id(self):
        """The user's tenant_id, if applicable."""
        return self.get('tenant_id')


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
