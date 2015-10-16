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

from oslo_config import cfg
from oslo_log import log
from poppy.common import cli

from poppy.provider.akamai.background_jobs.check_cert_status_and_update import \
    check_cert_status_and_update_flow

LOG = log.getLogger(__name__)

CLI_OPT = [
    cfg.StrOpt('domain_name',
               required=True,
               help='The domain you want to check cert status on'),
    cfg.StrOpt('cert_type',
               default='san',
               help='Cert type of this cert'),
    cfg.StrOpt('project_id',
               required=True,
               help='project id of this cert'),
    cfg.StrOpt('flavor_id',
               default='cdn',
               help='flavor id of this cert'),
]


@cli.runnable
def run():
    # TODO(kgriffs): For now, we have to use the global config
    # to pick up common options from openstack.common.log, since
    # that module uses the global CONF instance exclusively.
    conf = cfg.ConfigOpts()
    conf.register_cli_opts(CLI_OPT)
    conf(prog='akamai-cert-check')

    LOG.info('Starting to check status on domain: %s, for project_id: %s'
             'flavor_id: %s, cert_type: %s' %
             (
                 conf.domain_name,
                 conf.project_id,
                 conf.flavor_id,
                 conf.cert_type
             ))

    check_cert_status_and_update_flow.run_check_cert_status_and_update_flow(
        conf.domain_name,
        conf.cert_type,
        conf.flavor_id,
        conf.project_id
    )
