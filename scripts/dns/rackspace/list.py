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
import os
import re
import time

import pyrax


# read the config file
configParser = ConfigParser.RawConfigParser()
configFilePath = os.path.expanduser('~/.poppy/poppy.conf')
configParser.read(configFilePath)

# get the config parameters
username = configParser.get('drivers:dns:rackspace', 'username')
api_key = configParser.get('drivers:dns:rackspace', 'api_key')

# replace any single or double quotes from parameters
api_key = re.sub(r'^"|"$', '', api_key)
api_key = re.sub(r"^'|'$", '', api_key)
username = re.sub(r'^"|"$', '', username)
username = re.sub(r"^'|'$", '', username)

# Connect to Rackspace DNS using API key.
pyrax.set_setting("identity_type", "rackspace")
pyrax.set_credentials(username, api_key)
dns = pyrax.cloud_dns

num_domains = 0
for domain in dns.get_domain_iterator():
    if domain.name.startswith('cdn') and domain.name.endswith('.altcdn.com'):
        num_domains = num_domains + 1

        recs = domain.list_records()
        print("{0}: {1}".format(domain.name, len(recs)))

    time.sleep(2)

print("Total Number of Domains: {0}".format(num_domains))
