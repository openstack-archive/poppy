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
    if len(args) != 3:
        print("usage: python purge.py [env] [url]")
        print(
            "example : python purge.py [prod|test] http://blog.mysite.com/")
        sys.exit(2)

    env = args[1]
    url = args[2]

    config_parser = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/akamai.conf')
    config_parser.read(config_path)

    print("")
    print("")

    print("Purging assets: {0}".format(url))
    akamai_purge(env, config_parser, url)
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


def akamai_purge(env, config, url):
    purge_base_url = config.get(env, 'ccu_api_base_url')

    purge_url = ('{0}ccu/v2/queues/default'
                 .format(purge_base_url))

    print ("Purge URL: " + purge_url)
    data = {
        'objects': [url]
    }

    s = edge_session(env, config)

    response = s.post(
        purge_url,
        data=json.dumps(data),
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

    print("Status: {0}".format(response.status_code))
    pprint.pprint(response.headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    main(sys.argv)
