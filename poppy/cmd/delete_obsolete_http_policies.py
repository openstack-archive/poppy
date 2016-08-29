# Copyright (c) 2016 Rackspace, Inc.
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

import time

from oslo_config import cfg
from oslo_log import log

from poppy import bootstrap
from poppy.common import cli

LOG = log.getLogger(__name__)

CLI_OPT = [
    cfg.BoolOpt(
        'run_as_daemon',
        default=True,
        required=False,
        help='Run this script as a long running process.'
    ),
    cfg.IntOpt(
        'sleep_interval',
        default=60,
        required=False,
        help='Sleep interval between runs of http policy delete.'
    ),
]


@cli.runnable
def run():
    # TODO(kgriffs): For now, we have to use the global config
    # to pick up common options from openstack.common.log, since
    # that module uses the global CONF instance exclusively.
    conf = cfg.ConfigOpts()
    conf.register_cli_opts(CLI_OPT)
    log.register_options(conf)
    conf(project='poppy', prog='poppy')
    log.setup(conf, 'poppy')
    server = bootstrap.Bootstrap(conf)

    sleep_interval = conf.sleep_interval
    while True:
        (
            run_list,
            ignore_list
        ) = server.manager.background_job_controller.delete_http_policy()

        LOG.info(
            "Policies, attempting to delete {0}, ignored {0}".format(
                run_list, ignore_list))
        if conf.run_as_daemon is False:
            break
        time.sleep(sleep_interval)
