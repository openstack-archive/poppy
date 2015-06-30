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
import ConfigParser
import json
import os
import requests
import sys

from akamai.edgegrid import EdgeGridAuth


def main(args):
    if len(args) != 2:
        print("usage: python list_edgehostnames.py [env]")
        print(
            "example : python list_edgehostnames.py [prod|test]")
        sys.exit(2)

    env = args[1]

    config_parser = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/akamai.conf')
    config_parser.read(config_path)

    # print("querying akamai api for property hostnames: ")
    akamai_request(env, config_parser)


def edge_session(env, config):
    s = requests.Session()
    s.auth = EdgeGridAuth(
        # This is akamai credential
        client_token=config.get(env, 'client_token'),
        client_secret=config.get(env, 'client_secret'),
        access_token=config.get(env, 'access_token'))

    return s


def akamai_request(env, config):
    base_url = config.get(env, 'base_url')
    group_id = config.get(env, 'group_id')
    contract_id = config.get(env, 'contract_id')
    policy_num = config.get(env, 'policy_number')

    # get the latest version number
    version_url = (
        '{0}papi/v0/properties/prp_{1}/versions/' +
        '?contractId=ctr_{2}&groupId=grp_{3}')
    version_url = version_url.format(
        base_url,
        policy_num,
        contract_id,
        group_id
    )

    # print("Querying: ", version_url)
    s = edge_session(env, config)
    response = s.get(version_url,
                     headers={
                         'Content-type': 'application/json'
                     })
    version_dict = response.json()

    version_num = 1
    for item in version_dict['versions']['items']:
        if item['productionStatus'] == 'ACTIVE':
            version_num = item['propertyVersion']
            break

    # get the hostname information
    policy_url = (
        '{0}papi/v0/properties/prp_{1}/versions/{4}/hostnames/' +
        '?contractId=ctr_{2}&groupId=grp_{3}')
    policy_url = policy_url.format(
        base_url,
        policy_num,
        contract_id,
        group_id,
        version_num
    )

    # print("Querying: ", policy_url)
    s = edge_session(env, config)
    response = s.get(policy_url,
                     headers={
                         'Content-type': 'application/json'
                     })
    resp_dict = response.json()

    # print resp_dict
    domains_dict = {}
    for item in resp_dict['hostnames']['items']:
        domains_dict.setdefault(
            item['cnameTo'], list()).append(item['cnameFrom'])

    print(json.dumps(domains_dict, indent=4, sort_keys=True))

if __name__ == '__main__':
    main(sys.argv)
