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
from oslo_config import types

NonNegativeInt = types.Integer(min=0)

cfg.CONF.register_opts([
    cfg.StrOpt('project_id', help='the project used for all requests'),
    cfg.StrOpt('token', help='a valid token for the project_id'),
    cfg.StrOpt('host', help='the API endpoint'),
    cfg.Opt('min_wait', type=NonNegativeInt, default=1000,
            help='the min wait time between tasks in milliseconds'),
    cfg.Opt('max_wait', type=NonNegativeInt, default=1000,
            help='the max wait time between tasks in milliseconds'),
    cfg.ListOpt('flavors', default=['cdn'],
                help='a list of flavor ids to use for GETs'),
    cfg.BoolOpt('project_id_in_url', default=False,
                help='Use {host}/{project_id} as the base url'),
], group='test:perf')

cfg.CONF.register_opts([
    cfg.Opt("create_service", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("update_service_domain", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("update_service_rule", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("update_service_origin", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("delete_service", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("delete_asset", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("delete_all_assets", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("list_services", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("get_service", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("list_flavors", type=NonNegativeInt, default=0,
            help='the weight for this task'),
    cfg.Opt("get_flavors", type=NonNegativeInt, default=0,
            help='the weight for this task'),
], group='test:perf:weights')
