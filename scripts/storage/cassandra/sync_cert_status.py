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
import ssl
import sys

from cassandra import auth
from cassandra import cluster
from cassandra import query

from poppy.model import ssl_certificate

CQL_GET_ALL_CERTIFICATE_INFO = '''
    SELECT * FROM certificate_info
'''

CQL_INSERT_CERT_STATUS = '''
    INSERT INTO cert_status (domain_name,
        status
        )
    VALUES (%(domain_name)s,
        %(status)s)
'''


def cassandra_connection(env, config):
    ssl_options = None
    if config.getboolean(env, 'ssl_enabled'):
        ssl_options = dict()
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
    if config.getboolean(env, 'auth_enabled'):
        auth_provider = auth.PlainTextAuthProvider(
            username=config.get(env, 'username'),
            password=config.get(env, 'password')
        )

    cluster_connection = cluster.Cluster(
        config.get(env, 'cluster').split(","),
        auth_provider=auth_provider,
        port=config.getint(env, 'port'),
        ssl_options=ssl_options,
    )

    return cluster_connection


def synchronize_cert_status(session):
    session.execute('USE poppy')
    # TODO(obulpathi): Need a better way to select results,
    results = session.execute(CQL_GET_ALL_CERTIFICATE_INFO)
    certificates = []
    for result in results:
        if result.cert_details is not None:
            r_cert_details = {}
            # in case cert_details is None
            cert_details = result.cert_details or {}

            for key in cert_details:
                r_cert_details[key] = json.loads(cert_details[key])

            ssl_cert = ssl_certificate.SSLCertificate(
                domain_name=str(result.domain_name),
                flavor_id=str(result.flavor_id),
                cert_details=r_cert_details,
                cert_type=str(result.cert_type),
                project_id=str(result.project_id)
            )
            certificates.append(ssl_cert)

    print("Found the following certificates:\n")
    for certificate in certificates:
        print("{0} with status {1}".format(certificate.domain_name,
                                           certificate.get_cert_status()))

    for certificate in certificates:
        cert_args = {
            'domain_name': certificate.domain_name,
            'status': certificate.get_cert_status()
        }
        stmt = query.SimpleStatement(CQL_INSERT_CERT_STATUS)
        session.execute(stmt, cert_args)


def main(args):
    if len(args) != 2:
        print('Usage: python sync_cert_status.py [env]')
        print('Example : python sync_cert_status.py [prod|test]')
        sys.exit(2)

    env = args[1]

    config = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser('~/.poppy/cassandra.conf')
    config.read(config_path)

    print('')
    print('')

    print('Connecting to Cassandra')
    cluster_connection = cassandra_connection(env, config)
    session = cluster_connection.connect()
    if not session:
        print('Unable to connect to Cassandra, exiting')
        sys.exit(3)
    print('Connected with Cassandra')

    print('')
    print('')

    print('Updating cert_status to match certificate_info table ...')
    synchronize_cert_status(session)
    print('Finished updating cert_status.')
    session.cluster.shutdown()
    session.shutdown()

    print('')
    print('')


if __name__ == '__main__':
    main(sys.argv)
