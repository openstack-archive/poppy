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

SAN_CERT_RECORDS_FILE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))),
    'provider', 'akamai',
    'SAN_certs.data')


class PropertyUpdateTask(task.Task):
    default_provides = "update_version_and_service_list_info"

    def __init__(self):
        super(PropertyUpdateTask, self).__init__()
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller
        self.akamai_conf = self.akamai_driver.akamai_conf
        self.existing_hosts = []

    def execute(self):
        self.papi_job_list = self.sc.dequeue_all_papi_jobs()
        if len(self.papi_job_list) == 0:
            return
        update_version = self.get_update_version()
        print('Next version is: %s' % update_version)
        services_list = []
        update_hostnames = update_rules = False
        for papi_job in self.papi_job_list:
            papi_job_dict = json.loads(papi_job)
            print('Start doing PAPI job: %s' % str(papi_job_dict))
            # get a list of services_ids of this PAPI batch
            # needs to check if it a secure_host job
            # NOTE(tonytan4ever) : because of incosistenceies of MOD SAN
            # and custom cert, it is needed to use an or here
            services_list.extend(papi_job_dict.get('services_list_info', []) or
                                 papi_job_dict.get('message', {}).get(
                'services_list_info', []))
            # Handle hosts addition
            if papi_job_dict['j_type'] == 'hosts':
                update_hostnames = True
                if self.existing_hosts == []:
                    resp = self.akamai_driver.akamai_papi_api_client.get(
                        self.akamai_driver.akamai_papi_api_base_url.format(
                            middle_part='poperties/%s/versions/%s/hostnames' %
                            (self.akamai_conf['property_id'],
                             str(update_version)))
                    )
                    if resp.status_code != 200:
                        raise RuntimeError('PAPI API request failed.'
                                           'Exception: %s' % resp.text)
                    self.existing_hosts = json.loads(resp.text)['hostnames'][
                        'items']
                # message should be a list assembled hosts dictionary
                for action, host_info in json.loads(papi_job_dict['message']):
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
            if papi_job_dict['j_type'] == 'secureEdgeHost':
                update_hostnames = True
                resp = self.akamai_driver.akamai_papi_api_client.get(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='edgehostnames')
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                self.existing_edgehostnames = (
                    json.loads(resp.text)['edgeHostnames']['items'])
                for edgehostname in self.existing_edgehostnames:
                    if edgehostname['domainPrefix'] == (
                            papi_job_dict['message']['cnameHostname']):
                        if self.existing_hosts == []:
                            papi_api_client = (
                                self.akamai_driver.akamai_papi_api_client)
                            papi_base_url = (
                                self.akamai_driver.akamai_papi_api_base_url)
                            resp = papi_api_client.get(
                                papi_base_url.format(
                                    middle_part=(
                                        'properties/%s/versions/%s/hostnames' %
                                        (self.akamai_conf['property_id'],
                                         str(update_version)))
                                )
                            )
                            if resp.status_code != 200:
                                raise RuntimeError('PAPI API request failed.'
                                                   'Exception: %s' % resp.text)
                            self.existing_hosts = (
                                json.loads(resp.text)['hostnames']['items'])
                        self.existing_hosts.append({
                            "cnameType": "EDGE_HOSTNAME",
                            "edgeHostnameId": edgehostname['edgeHostnameId'],
                            # or edgehostname['cnameHostname']
                            "cnameFrom":  edgehostname['domainPrefix'],
                            'cnameTo': edgehostname['domainPrefix'] + (
                                '.edgekey.net')
                        })

                        if papi_job_dict['message']['certType'] == 'san':
                            self._update_san_cert_file(
                                edgehostname['domainPrefix'],
                                edgehostname['edgeHostnameId'])
                        break
                else:
                    raise ValueError("Cannot find secureEdgeHostname : %s" %
                                     papi_job_dict['message']['cnameHostname'])
            # Handle rules addition, such as Header-Forwarding etc.
            # Handle rules addition, such as Header-Forwarding etc.
            if papi_job_dict['j_type'] == 'rules':
                update_rules = True
                raise NotImplementedError
            # Origin SSL cert
            if papi_job_dict['j_type'] == 'origin-ssl-cert':
                update_rules = True
                raise NotImplementedError

        if update_hostnames:
            # This request needs json
            print('Start Updating Hostnames: %s' % str(self.existing_hosts))
            resp = self.akamai_driver.akamai_papi_api_client.put(
                self.akamai_driver.akamai_papi_api_base_url.format(
                    middle_part='properties/%s/versions/%s/hostnames' % (
                        self.akamai_conf['property_id'],
                        str(update_version))),
                data=json.dumps(self.existing_hosts),
                headers={'Content-type': 'application/json'}
            )

            if resp.status_code != 200:
                raise RuntimeError('PAPI API request failed.'
                                   'Exception: %s' % resp.text)

        if update_rules:
            # This request needs json
            # Right now not impelmented any rule update yet
            pass

        return update_version, services_list

    def get_update_version(self):
        """Get an Akamai property update version if necessary"""
        print('Starting to get next version for property: %s'
              % self.akamai_conf['property_id'])
        resp = self.akamai_driver.akamai_papi_api_client.get(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='properties/%s' % self.akamai_conf['property_id'])
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
                        middle_part='properties/%s/versions/%s' % (
                            self.akamai_conf['property_id'], str(max_version)))
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)
                etag = json.loads(resp.text)['versions']['items'][0]['etag']
                # create a new version
                resp = self.akamai_driver.akamai_papi_api_client.post(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='properties/%s/versions' % (
                            self.akamai_conf['property_id'])),
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

    def _update_san_cert_file(self, edgehostname, edgehostNameID):
        # Update the san cert info with edgehostname id
        san_cert_list = json.load(file(SAN_CERT_RECORDS_FILE_PATH))
        for san_cert_info in san_cert_list:
            if san_cert_info['cnameHostname'] == edgehostname:
                san_cert_info['edgeHostnameId'] = edgehostNameID
                break
        # Write this piece of san cert info the SAN_CERT_RECORDS_FILE_PATH
        with open(SAN_CERT_RECORDS_FILE_PATH, 'w') as san_cert_file:
            json.dump(san_cert_list, san_cert_file)

    def revert(self, **kwarg):
        # requeue all papi jobs here
        self.sc.requeue_papi_update_jobs(self.papi_job_list)


class PropertyActivateTask(task.Task):

    def __init__(self, rebind=[]):
        super(PropertyActivateTask, self).__init__(rebind=rebind)
        self.bootstrap_obj = bootstrap.Bootstrap(conf)
        self.akamai_driver = self.bootstrap_obj.manager.providers['akamai'].obj
        self.akamai_conf = self.akamai_driver.akamai_conf
        self.sc = self.akamai_driver.service_controller

    def execute(self, update_version_and_service_list_info):
        update_version, service_list_info = (
            update_version_and_service_list_info)
        # This request needs json
        print('Starting activating version: %s for property: %s' %
              (update_version,
               self.akamai_conf['property_id']))
        data = {
            'propertyVersion': update_version,
            'network': 'STAGING',
            'note': 'Updating configuration for property %s' % (
                self.akamai_conf['property_id']),
            'notifyEmails': [
                'admin@akamai.com',
                'tony.tan@rackspace.com'
            ],
        }
        resp = self.akamai_driver.akamai_papi_api_client.post(
            self.akamai_driver.akamai_papi_api_base_url.format(
                middle_part='properties/%s/activations' %
                self.akamai_conf['property_id']),
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
                    self.akamai_conf['property_id']),
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

        status_check_info, services_list = service_list_info
        status_check_info.update({
            'PropertyActivation': activation_id
        })
        print('Updating version: %s for property: %s in progress' %
              (update_version, self.akamai_conf['property_id']))
        print('Enqueue status check: %s, %s in progress' %
              (str(status_check_info), str(services_list)))
        self.sc.enqueue_status_check_queue(status_check_info, services_list)

    def revert(self, update_version_and_service_list_info, **kwargs):
        print('retrying...')
