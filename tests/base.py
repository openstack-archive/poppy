# Copyright (c) 2014 Rackspace Hosting, Inc.
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

import os

import fixtures
from oslo_config import cfg
import testtools


class TestCase(testtools.TestCase):
    """Child class of testtools.TestCase.

    Inherit from this and write your test methods. If the child class defines
    a prepare(self) method, this method will be called before executing each
    test method.
    """

    config_file = None

    def setUp(self):
        super(TestCase, self).setUp()

        self.useFixture(fixtures.FakeLogger('poppy'))

        if self.config_file:
            self.conf = self.load_conf(self.config_file)
        else:
            self.conf = cfg.ConfigOpts()

    @classmethod
    def conf_path(cls, filename):
        """Returns the full path to the specified conf file.

        :param filename: Name of the conf file to find (e.g.,
                         'wsgi_memory.conf')
        """

        if os.path.exists(filename):
            return filename

        return os.path.join(os.environ["CDN_TESTS_CONFIGS_DIR"], filename)

    @classmethod
    def load_conf(cls, filename):
        """Loads `filename` configuration file.

        :param filename: Name of the conf file to find (e.g.,
                         'wsgi_memory.conf')

        :returns: Project's config object.
        """
        conf = cfg.ConfigOpts()
        conf(args=[], default_config_files=[cls.conf_path(filename)])
        return conf
