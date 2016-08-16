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
from oslo_log import log

from taskflow import task

from poppy.distributed_task.utils import memoized_controllers


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
                # if the max version has not been activated yet
                # we just reuse the max version
                LOG.info("New version for : %s is %s" % (self.property_id,
                                                         str(max_version)))
                return max_version
            else:
                # retrieve the latest version from akamai
                resp = self.akamai_driver.akamai_papi_api_client.get(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='properties/%s/versions/%s' % (
                            self.property_id, str(max_version)))
                )
                if resp.status_code != 200:
                    raise RuntimeError('PAPI API request failed.'
                                       'Exception: %s' % resp.text)

                # if the latest version is pending state, stop execution
                production_status = \
                    json.loads(resp.text)['versions']['items'][0][
                        'productionStatus']

                if production_status.upper() == 'PENDING':
                    err_message = (
                        'Aborting task/flow execution.'
                        'Akamai property version {0} is in {1} status.'.format(
                            max_version,
                            production_status
                        )
                    )
                    LOG.error(err_message)
                    raise ValueError(err_message)

                etag = json.loads(resp.text)['versions']['items'][0]['etag']

                # now we need to create a new version (bump up a version)
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
                LOG.info("New version for : %s is %s" % (self.property_id,
                                                         str(max_version+1)))
                return max_version + 1


class PropertyUpdateTask(task.Task):
    default_provides = 'update_detail'

    def __init__(self):
        super(PropertyUpdateTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj
        self.sc = self.akamai_driver.service_controller
        self.akamai_conf = self.akamai_driver.akamai_conf

        self.existing_hosts = []
        self.existing_edgehostnames = []

    def execute(self, property_spec, new_version_number, update_type,
                update_info_list):
        """Update an Akamai property"""
        self.property_id = self.akamai_driver.papi_property_id(property_spec)

        update_info_list = json.loads(update_info_list)
        update_detail = ""

        # avoid loading hostnames multiple times
        if update_type == 'hostnames':
                if self.existing_hosts == []:
                    LOG.info("Getting Hostnames...")
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
                for action, update_cname_host_mapping_info in update_info_list:
                    update_detail_list = []
                    # add new hosts
                    if action == 'add':
                        for host_info in update_cname_host_mapping_info:
                            cnameToEdgeHostname = host_info['cnameTo']
                            # avoid loading edgehostnames multiple times
                            # we caching it to a class variable
                            if self.existing_edgehostnames == []:
                                LOG.info("Getting EdgeHostnames...")
                                resp = (
                                    self.akamai_driver.akamai_papi_api_client.
                                    get(
                                        self.akamai_driver.
                                        akamai_papi_api_base_url.format(
                                            middle_part='edgehostnames')
                                    ))

                                if resp.status_code != 200:
                                    raise RuntimeError('PAPI API request '
                                                       'failed.'
                                                       'Exception: %s' %
                                                       resp.text)
                                self.existing_edgehostnames = (
                                    json.loads(resp.text)['edgeHostnames'][
                                        'items']
                                )

                            for edgehostname in self.existing_edgehostnames:
                                if (edgehostname['domainPrefix'] ==
                                    cnameToEdgeHostname.replace(
                                        edgehostname['domainSuffix'], "")
                                        [:-1]):
                                    host_info['edgeHostnameId'] = (
                                        edgehostname['edgeHostnameId'])

                            self.existing_hosts.append(host_info)
                            update_detail_list.append(
                                "Add cnameFrom: %s to cnameTo %s" % (
                                    host_info['cnameFrom'],
                                    host_info['cnameTo'])
                            )
                        update_detail = ';'.join(update_detail_list)
                    # remove a hosts
                    elif action == 'remove':
                        update_detail_list = []
                        for host_info in update_cname_host_mapping_info:
                            for idx, existing_host_info in enumerate(
                                    self.existing_hosts):
                                if existing_host_info['cnameFrom'] == (
                                        host_info['cnameFrom']):
                                    del self.existing_hosts[idx]
                                    break
                            update_detail_list.append(
                                "Remove cnameFrom: %s to cnameTo %s"
                                % (host_info['cnameFrom'],
                                   host_info['cnameTo']))
                        update_detail = ';'.join(update_detail_list)

                LOG.info('Start Updating Hostnames: %s' %
                         str(self.existing_hosts))
                resp = self.akamai_driver.akamai_papi_api_client.put(
                    self.akamai_driver.akamai_papi_api_base_url.format(
                        middle_part='properties/%s/versions/%s/hostnames' % (
                            self.property_id,
                            str(new_version_number))),
                    data=json.dumps(self.existing_hosts),
                    headers={'Content-type': 'application/json'}
                )

                if resp.status_code != 200:
                    LOG.info("Updating property hostnames response code: %s" %
                             str(resp.status_code))
                    LOG.info("Updating property hostnames response text: %s" %
                             str(resp.text))
                else:
                    LOG.info("Update property hostnames successful...")
        # Handle secureEdgeHost addition
        elif update_type == 'secureEdgeHost':
            # Note(tonytan4ever): This will be used when adding custom cert
            pass
        elif update_type == 'rules':
            pass

        return update_detail


class PropertyActivateTask(task.Task):

    def __init__(self):
        super(PropertyActivateTask, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj
        self.akamai_conf = self.akamai_driver.akamai_conf
        self.sc = self.akamai_driver.service_controller

    def execute(self, property_spec, new_version_number, update_detail,
                notify_email_list=[]):
        """Update an Akamai property"""
        self.property_id = self.akamai_driver.papi_property_id(property_spec)

        # This request needs json
        LOG.info('Starting activating version: %s for property: %s' %
                 (new_version_number,
                  self.property_id))
        data = {
            'propertyVersion': new_version_number,
            'network': 'PRODUCTION',
            'note': 'Updating configuration for property %s: %s' % (
                self.property_id, update_detail),
            'notifyEmails': notify_email_list,
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
            LOG.info("response text: %s" % resp.text)
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

        # first get the activation id
        # activation id is inside of activation link itself
        activation_link = json.loads(resp.text)['activationLink']
        LOG.info("Activation link: %s" % activation_link)

        return {
            "activation_link": activation_link
        }

    def revert(self, property_spec, new_version_number, **kwargs):
        LOG.info('retrying task: %s ...' % self.name)


class MarkQueueItemsWithActivatedProperty(task.Task):

    def __init__(self):
        super(MarkQueueItemsWithActivatedProperty, self).__init__()
        service_controller, self.providers = \
            memoized_controllers.task_controllers('poppy', 'providers')
        self.akamai_driver = self.providers['akamai'].obj

    def execute(self, update_info_list):
        update_info_list = json.loads(update_info_list)

        queue_data = self.akamai_driver.san_mapping_queue.traverse_queue()
        new_queue_data = []
        for cert in queue_data:
            cert_dict = json.loads(cert)

            for action, update_cname_host_mapping_info in update_info_list:
                for host_info in update_cname_host_mapping_info:
                    if host_info['cnameFrom'] == cert_dict['domain_name']:
                        cert_dict['property_activated'] = True

            new_queue_data.append(json.dumps(cert_dict))

        self.akamai_driver.san_mapping_queue.put_queue_data(new_queue_data)
