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

from oslo_config import cfg
from oslo_context import context
import pecan
from pecan import hooks
import threading

_local_store = threading.local()


class PoppyRequestContext(context.RequestContext):

    def __init__(self, **kwargs):
        self.base_url = kwargs.pop('base_url')
        super(PoppyRequestContext, self).__init__(**kwargs)


class ContextHook(hooks.PecanHook):

    def before(self, state):
        context_kwargs = {}

        if 'X-Project-ID' in state.request.headers:
            context_kwargs['tenant'] = state.request.headers['X-Project-ID']
            context_kwargs['base_url'] = (
                state.request.host_url +
                '/'.join(state.request.path.split('/')[0:2]))
            # hack: if the configuration is set, the project_id
            # will be appended into the base_url
            if cfg.CONF.project_id_in_url:
                context_kwargs['base_url'] = '/'.join([
                    context_kwargs['base_url'],
                    state.request.headers['X-Project-ID']])

        if 'X-Auth-Token' in state.request.headers:
            context_kwargs['auth_token'] = (
                state.request.headers['X-Auth-Token']
            )

        # if we still dont have a tenant, then return a 400
        if 'tenant' not in context_kwargs:
            pecan.abort(400, detail="The Project ID must be provided.")

        request_context = PoppyRequestContext(**context_kwargs)
        state.request.context = request_context
        _local_store.context = request_context

        '''Attach tenant_id as a member variable project_id to controller.'''
        state.controller.__self__.project_id = getattr(_local_store.context,
                                                       "tenant", None)
        state.controller.__self__.base_url = getattr(_local_store.context,
                                                     "base_url", None)
        '''Attach auth_token as a member variable project_id to controller.'''
        state.controller.__self__.auth_token = getattr(_local_store.context,
                                                       "auth_token", None)
