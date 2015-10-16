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

import json

from oslo_config import cfg
from oslo_log import log

from poppy.common import cli
from poppy.provider.akamai.background_jobs.update_property import \
    update_property_flow

LOG = log.getLogger(__name__)

CLI_OPT = [
    cfg.StrOpt('domain_name',
               required=True,
               help='The domain you want to add in host name (cnameFrom)'),
    cfg.StrOpt('san_cert_name',
               required=True,
               help='Cert type of this cert'),
    cfg.StrOpt('update_type',
               default="hostsnames",
               help='Update type for this update, available types are:'
               'hostsnames, secureEdgeHost, rules'),
    cfg.StrOpt('action',
               default="add",
               help='What kind of action, do you want "add" or "remove" '
               'hostnames'),
    cfg.StrOpt('property_spec',
               default='akamai_https_san_config_numbers',
               help='Property spec of the property to be updated'),
    cfg.StrOpt('san_cert_domain_suffix',
               default='edgekey.net',
               help='Property spec of the property to be updated'),
]


@cli.runnable
def run():
    # TODO(kgriffs): For now, we have to use the global config
    # to pick up common options from openstack.common.log, since
    # that module uses the global CONF instance exclusively.
    conf = cfg.ConfigOpts()
    conf.register_cli_opts(CLI_OPT)
    conf(prog='akamai-papi-update')

    LOG.info("%s: %s to %s, on property: %s" % (
        conf.action,
        conf.domain_name,
        conf.san_cert_name,
        conf.property_spec
    ))

    update_info_list = json.dumps([
        (conf.action,
            {
                "cnameFrom": conf.domain_name,
                "cnameTo": '.'.join([conf.san_cert_name,
                                     conf.san_cert_domain_suffix]),
                "cnameType": "EDGE_HOSTNAME"
            })
    ])

    update_property_flow.run_update_property_flow(
        conf.property_spec, conf.update_type, update_info_list)
