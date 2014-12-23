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


schema_statements = [
    '''CREATE TABLE services (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    flavor_id VARCHAR,
    domains LIST<TEXT>,
    origins LIST<TEXT>,
    caching_rules LIST<TEXT>,
    restrictions LIST<TEXT>,
    provider_details MAP<TEXT, TEXT>,
    PRIMARY KEY (project_id, service_id)
    );
    ''',
    '''CREATE TABLE flavors (
    flavor_id VARCHAR,
    providers MAP<TEXT, TEXT>,
    PRIMARY KEY (flavor_id)
    );
    ''',
    '''CREATE TABLE service_names (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    PRIMARY KEY (service_name)
    );
    ''',
    '''CREATE TABLE archives (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    flavor_id VARCHAR,
    domains LIST<TEXT>,
    origins LIST<TEXT>,
    caching_rules LIST<TEXT>,
    restrictions LIST<TEXT>,
    provider_details MAP<TEXT, TEXT>,
    archived_time timestamp,
    PRIMARY KEY (project_id, service_id, archived_time)
    );
    '''
]
