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
import multiprocessing

import six

from poppy import bootstrap


@six.add_metaclass(abc.ABCMeta)
class Server(object):

    name = 'poppy-server'

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
            raise RuntimeError('Target not callable')

        self.process = multiprocessing.Process(target=target,
                                               name=self.name)
        self.process.daemon = True
        self.process.start()

        # Set the timeout. The calling thread will be blocked until the process
        # whose join() method is called terminates or until the timeout occurs.
        # The timeout is set, so that the calling (API tests)
        # & called processes (CDN Server) can execute in parallel.
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
    name = 'poppy-server'

    def get_target(self, conf):
        server = bootstrap.Bootstrap(conf)
        return server.run
