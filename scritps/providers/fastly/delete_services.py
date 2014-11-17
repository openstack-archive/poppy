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

import fastly


# get apikey
configParser = ConfigParser.RawConfigParser()
configFilePath = os.path.expanduser('~/.poppy/poppy.conf')
configParser.read(configFilePath)
apikey = configParser.get('drivers:provider:fastly', 'apikey')

# replace any single or double quotes from apikey
apikey = re.sub(r'^"|"$', '', apikey)
apikey = re.sub(r"^'|'$", '', apikey)

# Connects to Fastly using API key.
client = fastly.connect(apikey)

# List all services.
services = client.list_services()

for service in services:
    service_details = client.get_service_details(service.id)
    # if there is an active version, deactive it
    if service_details.active_version:
        client.deactivate_version(service.id,
                                  service_details.active_version['number'])
    client.delete_service(service.id)
