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

import ConfigParser
import json
import os
import pprint
import requests
import sys

from akamai.edgegrid import EdgeGridAuth


def main(args):
    if len(args) != 4:
        print("usage: python purge_status.py [env] [url] [purge_id]")
        print(
            "example : python purge_status.py [prod|test] "
            "http://blog.mysite.com/ 2424ada3-d964-11c4-8621-731adc86695c")
        sys.exit(2)

    env = args[1]
    purge_url = args[2]
    purge_id = args[3]

    config_parser = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/akamai.conf')
    config_parser.read(config_path)

    print("")
    print("")

    print("Fetching purge status")
    akamai_purge_status(env, config_parser, purge_url, purge_id)
    print("")
    print("")


def edge_session(env, config):
    s = requests.Session()
    s.auth = EdgeGridAuth(
        # This is akamai credential
        client_token=config.get(env, 'ccu_api_client_token'),
        client_secret=config.get(env, 'ccu_api_client_secret'),
        access_token=config.get(env, 'ccu_api_access_token'))

    return s


def akamai_purge_status(env, config, purge_url, purge_id):
    purge_base_url = config.get(env, 'ccu_api_base_url')

    purge_status_url = ('{0}ccu/v2/purges/{1}'
                        .format(purge_base_url, purge_id))

    print ("Purge URL: " + purge_url)
    print ("Purge ID: " + purge_id)
    data = {
        'objects': [purge_url]
    }

    s = edge_session(env, config)

    response = s.get(
        purge_status_url,
        data=json.dumps(data),
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

    print("Status: {0}".format(response.status_code))
    pprint.pprint(response.headers)
    pprint.pprint(response.json())

if __name__ == "__main__":
    main(sys.argv)
