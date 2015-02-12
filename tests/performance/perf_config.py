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
import os

config = ConfigParser.RawConfigParser()
config_path = os.path.expanduser('~/.poppy/perftest.conf')
config.read(config_path)

host = config.get('env', 'host')
min_wait = config.getint('env', 'min_wait')
max_wait = config.getint('env', 'max_wait')
token = config.get('env', 'token')
project_id = config.get('env', 'project_id')
project_id_in_url = config.getboolean('env', 'project_id_in_url')
flavor = config.get('env', 'flavor')

create_service = config.getint('test', 'create_service')
update_service_domain = config.getint('test', 'update_service_domain')
update_service_rule = config.getint('test', 'update_service_rule')
update_service_origin = config.getint('test', 'update_service_origin')
delete_service = config.getint('test', 'delete_service')
delete_asset = config.getint('test', 'delete_asset')
delete_all_assets = config.getint('test', 'delete_all_assets')
list_services = config.getint('test', 'list_services')
get_service = config.getint('test', 'get_service')
list_flavors = config.getint('test', 'list_flavors')
get_flavors = config.getint('test', 'get_flavors')
