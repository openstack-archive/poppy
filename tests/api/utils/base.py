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

import abc
import jsonschema
import multiprocessing
import six

from cafe.drivers.unittest import fixtures
from cdn import bootstrap

from tests.api.utils import client
from tests.api.utils import config


class TestBase(fixtures.BaseTestFixture):
    """Child class of fixtures.BaseTestFixture for testing CDN.

    Inherit from this and write your test methods. If the child class defines
    a prepare(self) method, this method will be called before executing each
    test method.
    """

    @classmethod
    def setUpClass(cls):

        super(TestBase, cls).setUpClass()

        cls.auth_config = config.authConfig()
        cls.auth_client = client.AuthClient()
        auth_token = cls.auth_client.get_auth_token(cls.auth_config.base_url,
                                                    cls.auth_config.user_name,
                                                    cls.auth_config.api_key)

        cls.config = config.cdnConfig()
        cls.url = cls.config.base_url

        cls.client = client.CDNClient(cls.url, auth_token,
                                      serialize_format='json',
                                      deserialize_format='json')

    def assertSchema(self, response_json, expected_schema):
        """Verify response schema aligns with the expected schema."""
        try:
            jsonschema.validate(response_json, expected_schema)
        except jsonschema.ValidationError as message:
            assert False, message

    @classmethod
    def tearDownClass(cls):
        """Deletes the added resources."""
        super(TestBase, cls).tearDownClass()


@six.add_metaclass(abc.ABCMeta)
class Server(object):

    name = "cdn-api-test-server"

    def __init__(self):
        self.process = None

    @abc.abstractmethod
    def get_target(self, conf):
        """Prepares the target object

        This method is meant to initialize server's
        bootstrap and return a callable to run the
        server.

        :param conf: The config instance for the
            bootstrap class
        :returns: A callable object
        """
        raise NotImplementedError

    def is_alive(self):
        """Returns True IF the server is running."""

        if self.process is None:
            return False

        return self.process.is_alive()

    def start(self, conf):
        """Starts the server process.

        :param conf: The config instance to use for
            the new process
        :returns: A `multiprocessing.Process` instance
        """

        target = self.get_target(conf)

        if not callable(target):
            raise RuntimeError("Target not callable")

        self.process = multiprocessing.Process(target=target,
                                               name=self.name)
        self.process.daemon = True
        self.process.start()

        # Give it a second to boot.
        self.process.join(1)
        return self.process

    def stop(self):
        """Terminates a process

        This method kills a process by
        calling `terminate`. Note that
        children of this process won't be
        terminated but become orphaned.
        """
        self.process.terminate()


class CDNServer(Server):
    name = "cdn-wsgiref-test-server"

    def get_target(self, conf):
        server = bootstrap.Bootstrap(conf)
        return server.run
