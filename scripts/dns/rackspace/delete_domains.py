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
project_id = configParser.get('drivers:dns:rackspace', 'project_id')
api_key = configParser.get('drivers:dns:rackspace', 'api_key')

# replace any single or double quotes from parameters
api_key = re.sub(r'^"|"$', '', api_key)
api_key = re.sub(r"^'|'$", '', api_key)
project_id = re.sub(r'^"|"$', '', project_id)
project_id = re.sub(r"^'|'$", '', project_id)

# Connect to Rackspace DNS using API key.
pyrax.set_setting("identity_type", "rackspace")
pyrax.set_credentials(project_id, api_key)
dns = pyrax.cloud_dns

for domain in dns.get_domain_iterator():
    print('Deleting {0}'.format(domain.name))
    try:
        dns.delete(domain)
    except pyrax.exceptions.NotFound:
        pass
    time.sleep(2)
