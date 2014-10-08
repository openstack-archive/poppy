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

from pecan import hooks

from poppy.openstack.common import context
from poppy.openstack.common import local


class PoppyRequestContext(context.RequestContext):

    def __init__(self, **kwargs):
        self.base_url = kwargs.pop('base_url')
        super(PoppyRequestContext, self).__init__(**kwargs)


class ContextHook(hooks.PecanHook):

    def on_route(self, state):
        context_kwargs = {}

        if 'X-Project-ID' in state.request.headers:
            context_kwargs['tenant'] = state.request.headers['X-Project-ID']
            context_kwargs['base_url'] = (
                state.request.host_url +
                '/'.join(state.request.path.split('/')[0:2]))

        if 'tenant' not in context_kwargs:
            # Didn't find the X-Project-Id header, pull from URL instead
            # Expects form /v1/{project_id}/path
            context_kwargs['tenant'] = state.request.path.split('/')[2]
            context_kwargs['base_url'] = (
                state.request.host_url +
                '/'.join(state.request.path.split('/')[0:3]))

        if 'X-Auth-Token' in state.request.headers:
            context_kwargs['auth_token'] = (
                state.request.headers['X-Auth-Token']
            )

        request_context = PoppyRequestContext(**context_kwargs)
        state.request.context = request_context
        local.store.context = request_context

    def before(self, state):
        '''Attach tenant_id as a member variable project_id to controller.'''
        state.controller.__self__.project_id = getattr(local.store.context,
                                                       "tenant", None)
        state.controller.__self__.base_url = getattr(local.store.context,
                                                     "base_url", None)
