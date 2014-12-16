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
import time

import requests


class HeatClient(object):

    def __init__(self, heat_url, token):
        self.heat_url = heat_url

        self.headers = {
            'content-type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-Token': token
        }

    def create_stack(self, yaml_path, stack_name, domain_name):
        """Creates a HEAT stack

        :param yaml_path: path to the uaml file relative to endtoend directory
            (eg. endtoend/heat_file.yaml)
        :param stack_name: name of the heat stack containing the test site
        :param domain_name: domain name to use for the deployed website
        :returns: response to HEAT API call
        """
        url = self.heat_url + '/stacks'

        template_file = open(yaml_path, 'r+')
        template = template_file.read()
        template = template.replace('example.com', domain_name)
        request_data = {
            "stack_name": stack_name,
            "disable_rollback": True,
            "parameters": {},
            "template": template,
            "timeout_mins": 60
        }

        response = requests.post(url,
                                 data=json.dumps(request_data),
                                 headers=self.headers)
        return response

    def get_stack_details(self, stack_name):
        """Gets details of the stack

        :param stack_name: name of the stack to be queried
        :returns: response containing stack details
        """
        url = self.heat_url + '/stacks/' + stack_name
        response = requests.get(url, headers=self.headers)
        return response

    def wait_for_stack_status(self, stack_name, status='CREATE_COMPLETE',
                              retry_timeout=6000, retry_interval=10):
        """Wait for the stack to reach the specified status

        :param stack_name: name of the stack to be queried
        :param status: desired stack status
        :param retry_interval: how frequently to ping for status change(sec)
        :param retry_interval: max number of seconds to wait for status change
        :returns: None
        """
        current_status = ''
        start_time = int(time.time())
        stop_time = start_time + retry_timeout
        while current_status != status:
            time.sleep(retry_interval)
            stack_details = self.get_stack_details(stack_name=stack_name)
            body = stack_details.json()
            current_status = body['stack']['stack_status']
            if (current_status == status):
                return
            current_time = int(time.time())
            if current_time > stop_time:
                return

    def get_server_ip(self, stack_name):
        """Get the cloud server ip for the stack_name

        :param stack_name: name of the stack
        :returns: ip of the server that is part of the stack
        """
        stack_details = self.get_stack_details(stack_name)
        stack_details = stack_details.json()
        outputs = stack_details['stack']['outputs']
        server_ip = [output['output_value'] for
                     output in outputs if
                     output['output_key'] == 'server_ip']
        return server_ip[0]

    def delete_stack(self, stack_name):
        """Delete specified stack

        :param stack_name: name of the stack
        :returns: DELETE response
        """
        url = self.heat_url + '/stacks/' + stack_name
        response = requests.delete(url, headers=self.headers)
        return response
