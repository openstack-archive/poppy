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
from taskflow import task

from poppy.distributed_task.utils import memoized_controllers
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class PropertyGetLatestVersionTask(task.Task):
    default_provides = "new_version_number"

    def __init__(self):
        super(PropertyGetLatestVersionTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller
        self.akamai_conf = self.akamai_driver.akamai_conf

    def execute(self, property_spec):
        """Get/Create a new Akamai property update version if necessary"""
        self.property_id = self.akamai_driver.papi_property_id(property_spec)

        LOG.info('Starting to get next version for property: %s'
                 % self.property_id)
        resp = self.akamai_driver.akamai_papi_api_client.get(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='properties/%s' % self.property_id)
        )
        if resp.status_code != 200:
            raise RuntimeError('PAPI API request failed.'
                               'Exception: %s' % resp.text)
        else:
            a_property = json.loads(resp.text)['properties']['items'][0]
            latestVersion = a_property['latestVersion'] or 0
            production_version = a_property['productionVersion'] or -1
            staging_version = a_property['stagingVersion'] or -1

            max_version = max(latestVersion, production_version,
                              staging_version)

            if production_version == -1 and staging_version == -1:
                # if the max version has not been activated yet     199
                # we just reuse the max version     200
                return max_version
            else:
                # else new need to create a new version (bump up a version)
                resp = self.akamai_driver.akamai_papi_api_client.get(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='properties/%s/versions/%s' % (
                            self.property_id, str(max_version)))
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                etag = json.loads(resp.text)['versions']['items'][0]['etag']
                # create a new version
                resp = self.akamai_driver.akamai_papi_api_client.post(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='properties/%s/versions' % (
                            self.property_id)),
                    data=json.dumps({
                        'createFromVersion': max_version,
                        'createFromEtag': etag
                    }),
                    headers={'Content-type': 'application/json'}
                )

                if resp.status_code != 201:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                return max_version+1


class PropertyUpdateTask(task.Task):

    def __init__(self):
        super(PropertyUpdateVersionTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller
        self.akamai_conf = self.akamai_driver.akamai_conf

    def execute(self, property_spec, new_version_number, update_type,
                update_info):
        """Update an Akamai property"""
        self.property_id = self.akamai_driver.papi_property_id(property_spec)

        update_inf_dict = json.loads(update_info)

        if update_type == 'hostsnames':
                if self.existing_hosts == []:
                    resp = self.akamai_driver.akamai_papi_api_client.get(
                        self.akamai_driver.akamai_papi_api_base_url.format(
                            middle_part='properties/%s/versions/%s/hostnames' %
                            (self.property_id,
                             str(new_version_number)))
                    )
                    if resp.status_code != 200:
                        raise RuntimeError('PAPI API request failed.'
                                           'Exception: %s' % resp.text)
                    self.existing_hosts = json.loads(resp.text)['hostnames'][
                        'items']
                # message should be a list assembled hosts dictionary
                for action, host_info in json.loads(update_inf_dict['message']):
                    # add new hosts
                    if action == 'add':
                        self.existing_hosts.append(host_info)
                    # remove a hosts
                    if action == 'remove':
                        for idx, existing_host_info in enumerate(
                                self.existing_hosts):
                            if existing_host_info['cnameFrom'] == (
                                    host_info['cnameFrom']):
                                del self.existing_hosts[idx]
                                break

        # Handle secureEdgeHost addition
        if update_type == 'secureEdgeHost':
            # Note(tonytan4ever): This will be used when adding custom cert
            pass

        if update_type == 'rules':
            pass


class PropertyActivateTask(task.Task):

    def __init__(self):
        super(PropertyActivateTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj
        self.akamai_conf = self.akamai_driver.akamai_conf
        self.sc = self.akamai_driver.service_controller

    def execute(self, property_spec, new_version_number):
        """Update an Akamai property"""
        self.property_id = self.akamai_driver.papi_property_id(property_spec)

        # This request needs json
        LOG.info('Starting activating version: %s for property: %s' %
                 (new_version_number,
                  self.property_id))
        data = {
            'propertyVersion': new_version_number,
            'network': 'STAGING',
            'note': 'Updating configuration for property %s' % (
                self.property_id),
            'notifyEmails': [
                'admin@akamai.com',
                'cdn@rackspace.com'
            ],
        }
        resp = self.akamai_driver.akamai_papi_api_client.post(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='properties/%s/activations' %
                self.property_id),
            data=json.dumps(data),
            headers={'Content-type': 'application/json'}
        )
        # Here activation API call will return a 400,
        # with all the messageIds need to handle that not as
        # an exception
        if resp.status_code != 201 and resp.status_code != 400:
            raise RuntimeError('PAPI API request failed.'
                               'Exception: %s' % resp.text)
        # else extract out all the warnings
        # acknowledgementWarning
        if resp.status_code == 400:
            warnings = [warning['messageId'] for warning in
                        json.loads(resp.text)['warnings']]
            data['acknowledgeWarnings'] = warnings
            resp = self.akamai_driver.akamai_papi_api_client.post(
                self.akamai_driver.akamai_papi_api_base_url.format(
                    middle_part='properties/%s/activations/' %
                    self.property_id),
                data=json.dumps(data),
                headers={'Content-type': 'application/json'}
            )
            if resp.status_code != 201:
                raise RuntimeError('PAPI API request failed.'
                                   'Exception: %s' % resp.text)

        # enqueue status check queue
        # first get the activation id
        activation_link = json.loads(resp.text)['activationLink']
        activation_id = activation_link.split('?')[0].split('/')[-1]

    def revert(self, update_version_and_service_list_info, **kwargs):
        print('retrying...')
