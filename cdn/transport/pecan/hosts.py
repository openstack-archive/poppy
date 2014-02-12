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

from pecan import expose, response
from pecan.rest import RestController


class HostsController(RestController):

    @expose('json')
    def get_all(self):
        '''return the list of hostnames
        '''
        return dict(
            hostname='www.sample.com'
        )

    @expose('json')
    def get(self, id):
        '''return the configuration of the hostname
        '''
        return dict(
            hostname=id,
            description='My Sample Website'
        )

    @expose('json')
    def put(self, id):
        '''add the hostname
        '''

        response.status = 201
        return dict(
            hostname=id,
            description='My Sample Website'
        )

    @expose('json')
    def delete(self, id):
        '''delete the hostname
        '''
        response.status = 204
        return None
