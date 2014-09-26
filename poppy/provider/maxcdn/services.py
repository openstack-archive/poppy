# Copyright (c) 2013 Rackspace, Inc.
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

import hashlib
import re

from poppy.common import decorators
from poppy.provider import base

MAXCDN_NAMING_REGEX = re.compile('^[a-zA-Z0-9-]{3,32}$')


class ServiceController(base.ServiceBase):

    '''MaxCDN Service Controller.

    '''

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        '''Initialize a service controller object.'''
        super(ServiceController, self).__init__(driver)

        self.driver = driver

    def update(self, pullzone_id, service_obj):
        '''MaxCDN update.

         manager needs to pass in pullzone id to delete.
        '''
        try:
            # TODO(tonytan4ever): correctly convert and update service_obj
            # to a dictionary passed into maxcdn call.
            update_response = self.client.put('/zones/pull.json/%s'
                                              % pullzone_id,
                                              params=service_obj.to_dict())
            if update_response['code'] != 200:
                return self.responder.failed('failed to update service')
            return self.responder.updated(
                update_response['data']['pullzone']['id'])
        except Exception:
            # this exception branch will most likely for a network failure
            return self.responder.failed('failed to update service')

    def create(self, service_obj):
        '''MaxCDN create.

         manager needs to pass in a service name to create.
        '''
        try:
            # Create a new pull zone: maxcdn only supports 1 origin
            origin = service_obj.origins[0]
            origin_prefix = 'https://' if origin.ssl else 'http://'
            create_response = self.client.post('/zones/pull.json', data={
                'name': self._map_service_name(service_obj.name),
                # TODO(tonytan4ever): maxcdn takes origin with
                # 'http://' or 'https://' prefix.
                'url': ''.join([origin_prefix, origin.origin]),
                'port': getattr(origin, 'port', 80),
            })

            if create_response['code'] != 201:
                return self.responder.failed('failed to create service')

            created_zone_info = create_response['data']['pullzone']

            # Add custom domains to this service
            links = []
            for domain in service_obj.domains:
                self.client.post(
                    '/zones/pull/%s/customdomains.json'
                    % created_zone_info['id'],
                    {'custom_domain': domain.domain})
                links.append({'href': domain.domain, "rel": "access_url"})
            # TODO(tonytan4ever): What if it fails during add domains ?
            return self.responder.created(created_zone_info['id'], links)
        except Exception:
            # this exception branch will most likely for a network failure
            return self.responder.failed('failed to create service')

    def delete(self, pullzone_id):
        '''MaxCDN create.

         manager needs to pass in a service name to delete.
        '''
        try:
            delete_response = self.client.delete('/zones/pull.json/%s'
                                                 % pullzone_id)
            if delete_response['code'] != 200:
                return self.responder.failed('failed to delete service')
            return self.responder.deleted(pullzone_id)
        except Exception:
            # this exception branch will most likely for a network failure
            return self.responder.failed('failed to delete service')

    # TODO(tonytan4ever): get service
    def get(self, service_name):
        '''Get details of the service, as stored by the provider.'''
        return {'domains': [], 'origins': [], 'caching': []}

    def _map_service_name(self, service_name):
        """Map poppy service name to provider's specific service name.

        Map a poppy service name to a provider's service name so it
        can comply provider's naming convention.
        """
        if MAXCDN_NAMING_REGEX.match(service_name):
            return service_name
        else:
            return hashlib.sha1(service_name.encode("utf-8")).hexdigest()[:30]

    @decorators.lazy_property(write=False)
    def current_customer(self):
        # This returns the current customer account info
        account_info_return = self.client.get('/account.json')
        if account_info_return['code'] == 200:
            return account_info_return['data']['account']
        else:
            raise RuntimeError("Get maxcdn current customer failed...")
