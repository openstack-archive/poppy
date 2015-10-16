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

from poppy import bootstrap


LOG = log.getLogger(__name__)
conf = cfg.CONF

try:
    getattr(conf, 'log_config_append')
except cfg.NoSuchOptError:
    # NOTE(TheSriram): Only register options, if they
    # havent already been registered.
    log.register_options(conf)

conf(project='poppy', prog='poppy', args=[])


def memoize(f):
    memo = {}

    def helper(*args, **kwargs):
        x = str(args) + str(kwargs)
        if x not in memo:
            memo[x] = f(*args, **kwargs)
        return memo[x]

    return helper


@memoize
def task_controllers(program, controller=None):
    bootstrap_obj = bootstrap.Bootstrap(conf)
    service_controller = bootstrap_obj.manager.services_controller

    if controller == 'storage':
        return service_controller, service_controller.storage_controller
    if controller == 'dns':
        return service_controller, service_controller.dns_controller
    if controller == 'providers':
        return service_controller, bootstrap_obj.manager.providers
    if controller == 'ssl_certificate':
        return service_controller, (
            bootstrap_obj.manager.ssl_certificate_controller)
    else:
        return service_controller
