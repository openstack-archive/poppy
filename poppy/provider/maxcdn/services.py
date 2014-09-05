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

from poppy.provider import base


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

        # This returns the current customer account info
        account_info_return = self.client.get('/account.json')
        if account_info_return['code'] != 200:
            raise RuntimeError(account_info_return['error'])
        self.current_customer = account_info_return['data']['account']

    def update(self, pullzone_id, service_json):
        '''MaxCDN update.

         manager needs to pass in pullzone id to delete.
        '''
        try:
            update_response = self.client.put('/zones/pull.json/%s'
                                              % pullzone_id,
                                              params=service_json)
            if update_response['code'] != 200:
                return self.responder.failed('failed to update service')
            return self.responder.updated(
                update_response['data']['pullzone']['id'])
        except Exception:
            # this exception branch will most likely for a network failure
            return self.responder.failed('failed to update service')

    def create(self, service_name, service_json):
        '''MaxCDN create.

         manager needs to pass in a service name to create.
        '''
        try:
            # Create a new pull zone: maxcdn only supports 1 origin
            origin = service_json['origins'][0]
            create_response = self.client.post('/zones/pull.json', data={
                'name': service_name,
                'url': origin['origin'],
                'port': origin.get('port', 80),
                'sslshared': 1 if origin['ssl'] else 0,
            })

            if create_response['code'] != 201:
                return self.responder.failed('failed to create service')

            created_zone_info = create_response['data']['pullzone']

            # Add custom domains to this service
            links = []
            for domain in service_json['domains']:
                self.client.post(
                    '/zones/pull/%s/customdomains.json'
                    % created_zone_info['id'],
                    {'custom_domain': domain['domain']})
                links.append({'href': domain['domain'], "rel": "access_url"})
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
