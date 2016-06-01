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

try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover

from poppy.transport.pecan.models.response import link


class DNSModel(collections.OrderedDict):
    def __init__(self, is_alive):
        super(DNSModel, self).__init__()

        if is_alive:
            self['online'] = 'true'
        else:
            self['online'] = 'false'


class StorageModel(collections.OrderedDict):
    def __init__(self, is_alive):
        super(StorageModel, self).__init__()

        if is_alive:
            self['online'] = 'true'
        else:
            self['online'] = 'false'


class DistributedTaskModel(collections.OrderedDict):
    def __init__(self, is_alive):
        super(DistributedTaskModel, self).__init__()

        if is_alive:
            self['online'] = 'true'
        else:
            self['online'] = 'false'


class ProviderModel(collections.OrderedDict):
    def __init__(self, is_alive):
        super(ProviderModel, self).__init__()

        if is_alive:
            self['online'] = 'true'
        else:
            self['online'] = 'false'


class HealthModel(collections.OrderedDict):

    def __init__(self, controller, health_map):
        super(HealthModel, self).__init__()

        health_dns = collections.OrderedDict()
        if health_map['dns']['is_alive']:
            health_dns['online'] = 'true'
        else:
            health_dns['online'] = 'false'

        health_dns['links'] = link.Model(
            u'{0}/health/dns/{1}'.format(
                controller.base_url, health_map['dns']['dns_name']),
            'self')

        self['dns'] = {
            health_map['dns']['dns_name']: health_dns}

        health_storage = collections.OrderedDict()
        if health_map['storage']['is_alive']:
            health_storage['online'] = 'true'
        else:
            health_storage['online'] = 'false'

        health_storage['links'] = link.Model(
            u'{0}/health/storage/{1}'.format(
                controller.base_url, health_map['storage']['storage_name']),
            'self')

        self['storage'] = {
            health_map['storage']['storage_name']: health_storage}

        health_distributed_task = collections.OrderedDict()
        if health_map['distributed_task']['is_alive']:
            health_distributed_task['online'] = 'true'
        else:
            health_distributed_task['online'] = 'false'

        health_distributed_task['links'] = link.Model(
            u'{0}/health/distributed_task/{1}'.format(
                controller.base_url,
                health_map['distributed_task']['distributed_task_name']),
            'self')

        self['distributed_task'] = {
            health_map['distributed_task']['distributed_task_name']:
                health_distributed_task}

        self['providers'] = {}
        for provider in health_map['providers']:
            health_provider = collections.OrderedDict()
            if provider['is_alive']:
                health_provider['online'] = 'true'
            else:
                health_provider['online'] = 'false'

            health_provider['links'] = link.Model(
                u'{0}/health/provider/{1}'.format(
                    controller.base_url, provider['provider_name']),
                'self')

            self['providers'][provider['provider_name']] = health_provider
