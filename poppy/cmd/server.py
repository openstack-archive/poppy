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
import os

from oslo_config import cfg
from oslo_log import log

from poppy import bootstrap
from poppy.common import cli


@cli.runnable
def run():
    # TODO(kgriffs): For now, we have to use the global config
    # to pick up common options from openstack.common.log, since
    # that module uses the global CONF instance exclusively.
    conf = cfg.CONF
    log.register_options(conf)
    conf(project='poppy', prog='poppy')
    log.setup(conf, 'poppy')
    server = bootstrap.Bootstrap(conf)

    # The following code is to daemonize poppy-server to avoid
    # an issue with wsgiref writing to stdout/stderr when we don't
    # want it to.  This is specifically needed to allow poppy to
    # run under devstack, but it may also be useful for other scenarios.
    # Open /dev/zero and /dev/null for redirection.
    # Daemonizing poppy-server is needed *just* when running under devstack
    # and when poppy is invoked with `daemon` command line option.
    if conf.daemon:
        zerofd = os.open('/dev/zero', os.O_RDONLY)
        nullfd = os.open('/dev/null', os.O_WRONLY)

        # Close the stdthings and reassociate them with a non terminal
        os.dup2(zerofd, 0)
        os.dup2(nullfd, 1)
        os.dup2(nullfd, 2)

        # Detach process context, this requires 2 forks.
        try:
            pid = os.fork()
            if pid > 0:
                os._exit(0)
        except OSError:
            os._exit(1)

        try:
            pid = os.fork()
            if pid > 0:
                os._exit(0)
        except OSError:
            os._exit(2)
    server.run()
