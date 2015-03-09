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

import json
import os

from oslo.config import cfg
from taskflow import task

from poppy import bootstrap
from poppy.openstack.common import log


LOG = log.getLogger(__name__)
conf = cfg.CONF
conf(project='poppy', prog='poppy', args=[])


class PropertyUpdateTask(task.Task):
    default_provides = "update_version"

    def __init__(self):
        super(PropertyUpdateTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.sc = (
            self.bootstrap_obj.manager.distributed_task.services_controller)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai']
        self.akamai_conf = self.akamai_driver.akamai_conf

    def execute(self):
        self.papi_job_list = self.sc.dequeue_all_papi_update_job()
        update_version = self.get_update_version()
        for papi_job in self.papi_job_list:
            papi_job_dict = json.loads(papi_job)
            # Handle hosts addition
            if papi_job_dict['j_type'] == 'hosts':
                resp = self.akamai_driver.akamai_papi_api_client.get(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='poperties/%s/versions/%s' % (
                            self.akamai_conf['property_id'],
                            str(update_version)))
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                existing_hosts = json.loads(resp.text)['hostnames']['items']
                # message should be a list assembled hosts dictionary
                existing_hosts.extends(papi_job_dict['message'])
                # This request needs json
                resp = self.akamai_driver.akamai_papi_api_client.put(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='poperties/%s/versions/%s' % (
                            self.akamai_conf['property_id'],
                            str(update_version))),
                    data=json.dumps(existing_hosts),
                    headers={'Content-type': 'application/json'}
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
            # Handle rules addition, such as Header-Forwarding etc.
            if papi_job_dict['j_type'] == 'rules':
                raise NotImplementedError
            # Origin SSL cert
            if papi_job_dict['j_type'] == 'origin-ssl-cert':
                raise NotImplementedError

        return update_version

    def get_update_version(self):
        """Get an Akamai property update version if necessary"""
        resp = self.akamai_driver.akamai_papi_api_client.get(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='poperties/%s' % self.akamai_conf['property_id'])
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
                # if the max version has not been activated yet
                # we just reuse the max version
                return max_version
            else:
                # else new need to create a new version (bump up a version)
                resp = self.akamai_driver.akamai_papi_api_client.get(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='poperties/%s/versions/%s' % (
                            self.akamai_conf['property_id'], str(max_version)))
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                etag = json.loads(resp.text)['versions']['items'][0]['etag']
                # create a new version
                resp = self.akamai_driver.akamai_papi_api_client.post(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='poperties/%s/versions' % (
                            self.akamai_conf['property_id'])),
                    data={
                        'createFromVersion': max_version,
                        'createFromEtag': etag
                    }
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                return max_version+1

    def revert(self):
        # requeue all papi jobs here
        self.sc.requeue_papi_update_jobs(self.papi_job_list)


class PropertyActivateTask(task.Task):

    def __init__(self):
        super(PropertyUpdateTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai']
        self.akamai_conf = self.akamai_driver.akamai_conf

    def execute(self, update_version):
        # This request needs json
        data = {
            'propertyVersion': update_version,
            'network': 'STAGING',
            'note': 'Updating configuration for property %s' % (
                self.akamai_conf['property_id']),
            'notifyEmails': [
                'admin@akamai.com',
                'admin@rackspace.com'
            ],
        }
        resp = self.akamai_driver.akamai_papi_api_client.put(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='poperties/%s/activations/%s' % (
                    self.akamai_conf['property_id'],
                    str(update_version))),
            data=json.dumps(data),
            headers={'Content-type': 'application/json'}
        )
        if resp.status_code != 200:
            raise RuntimeError('PAPI API request failed.'
                               'Exception: %s' % resp.text)
        # else extract out all the warnings
        # acknowledgementWarning
        warnings = [warning['messageId'] for warning in
                    json.loads(resp.text)['warnings']]
        data['acknowledgeWarnings'] = warnings
        resp = self.akamai_driver.akamai_papi_api_client.put(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='poperties/%s/activations/%s' % (
                    self.akamai_conf['property_id'],
                    str(update_version))),
            data=json.dumps(data.extends),
            headers={'Content-type': 'application/json'}
        )
        if resp.status_code != 200:
            raise RuntimeError('PAPI API request failed.'
                               'Exception: %s' % resp.text)

    def revert(self):
        LOG.info('retrying...')
