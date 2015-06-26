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
    if len(args) != 3:
        print("usage: python put.py [env] [domain]")
        print(
            "example : python put.py [prod|test|prod_staging] www.mysite.com")
        sys.exit(2)

    env = args[1].replace('_staging', '')
    use_staging = args[1].endswith('_staging')
    domain = args[2]

    config_parser = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/akamai.conf')
    config_parser.read(config_path)

    print("")
    print("")

    print("updating api with policy definition: ")
    akamai_request(env, domain, use_staging, config_parser)
    print("")
    print("")


def edge_session(env, config):
    s = requests.Session()
    s.auth = EdgeGridAuth(
        # This is akamai credential
        client_token=config.get(env, 'client_token'),
        client_secret=config.get(env, 'client_secret'),
        access_token=config.get(env, 'access_token'))

    return s


def akamai_request(env, domain, use_staging, config):
    base_url = config.get(env, 'base_url')
    policy_num = config.get(env, 'policy_number')

    env_var = "production"
    if use_staging:
        env_var = "staging"

    policy_url = ('{0}partner-api/v1/network/{3}/properties/'
                  '{1}/sub-properties/{2}/policy')
    policy_url = policy_url.format(
        base_url,
        policy_num,
        domain,
        env_var
    )

    print ("API URL: " + policy_url)
    print ("ARLID: " + str(policy_num))

    s = edge_session(env, config)
    data = {
        "rules": [
            {
                "behaviors": [
                    {
                        "name": "origin",
                        "params": {
                            "cacheKeyType": "digital_property",
                            "cacheKeyValue": "-",
                            "digitalProperty": domain,
                            "hostHeaderType": "digital_property",
                            "hostHeaderValue": "-",
                            "originDomain": domain
                        },
                        "value": "-"
                    },
                    {
                        "name": "caching",
                        "type": "fixed",
                        "value": "172800s"
                    }
                ],
                "matches": [
                    {
                        "name": "url-wildcard",
                        "value": "/*"
                    }
                ]
            }
        ]
    }

    response = s.put(
        policy_url,
        data=json.dumps(data),
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

    print(response.status_code)
    resp_dict = json.loads(response.text)
    print(json.dumps(resp_dict, indent=4, sort_keys=True))


if __name__ == '__main__':
    main(sys.argv)
