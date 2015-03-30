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
import ssl
import sys

from cassandra import auth
from cassandra import cluster


DELETE_NULLS = '''
    DELETE FROM services WHERE project_id = ? AND service_id = ?
    '''


def cassandra_connection(env, config):
    ssl_options = None
    if config.get(env, 'ssl_enabled'):
        ssl_options = {}
        ssl_options['ca_certs'] = config.get(env, 'ssl_ca_certs')
        ssl_options['ssl_version'] = config.get(env, 'ssl_version')
        if ssl_options['ssl_version'] == 'TLSv1':
            ssl_options['ssl_version'] = ssl.PROTOCOL_TLSv1
        elif ssl_options['ssl_version'] == 'TLSv1.1':
            ssl_options['ssl_version'] = ssl.PROTOCOL_TLSv1_1
        elif ssl_options['ssl_version'] == 'TLSv1.2':
            ssl_options['ssl_version'] = ssl.PROTOCOL_TLSv1_2
        else:
            print('Unknown SSL Version')
            sys.exit(4)

    auth_provider = None
    if config.get(env, 'auth_enabled'):
        auth_provider = auth.PlainTextAuthProvider(
            username=config.get(env, 'username'),
            password=config.get(env, 'password')
        )

    cluster_connection = cluster.Cluster(
        config.get(env, 'cluster').split(","),
        auth_provider=auth_provider,
        port=config.get(env, 'port'),
        ssl_options=ssl_options,
    )

    return cluster_connection


def delete(session):
    session.execute('USE poppy')
    # TODO(obulpathi): Need a better way to select results,
    # especially for large number of services
    results = session.execute('SELECT * FROM services')
    services = []
    for result in results:
        if result.service_name is None:
            services.append([result.project_id, result.service_id])

    print("Deleting following services:\n")
    print("Project Id\t Service Id \n")
    for service in services:
        print("{0}\t{1}".format(service[0], service[1]))
    for service in services:
        prepared_stmt = session.prepare(DELETE_NULLS)
        bound_stmt = prepared_stmt.bind(service)
        session.execute(bound_stmt)


def main(args):
    if len(args) != 2:
        print('Usage: python delete_service_name_nulls.py [env]')
        print('Example : python delete_service_name_nulls.py [prod|test]')
        sys.exit(2)

    env = args[1]

    config = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/cassandra.conf')
    config.read(config_path)

    print('')
    print('')

    print('Connecting with Cassandra')
    cluster_connection = cassandra_connection(env, config)
    session = cluster_connection.connect()
    if not session:
        print('Unable to connect to Cassandra, exiting')
        sys.exit(3)
    print('Connected with Cassandra')

    print('')
    print('')

    print('Deleting services with service_name null')
    delete(session)
    print('Deleted services with service_name null')
    session.cluster.shutdown()
    session.shutdown()

    print('')
    print('')


if __name__ == '__main__':
    main(sys.argv)
