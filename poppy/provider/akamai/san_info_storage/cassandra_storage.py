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

import copy
import json
import os
import ssl

import cassandra
from cassandra import auth
from cassandra import cluster
from cassandra import policies
from cassandra import query
from cdeploy import migrator
from oslo_config import cfg
from oslo_log import log

from poppy.common import decorators
from poppy.provider.akamai.san_info_storage import base


_DEFAULT_OPTIONS = [
    cfg.StrOpt('datacenter', default='',
               help='Host datacenter of the API'),
    cfg.BoolOpt('use_same_storage_driver', default=True,
                help='Whether to use the same poppy storage driver')
]

CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default=['127.0.0.1'],
                help='Cassandra cluster contact points'),
    cfg.IntOpt('port', default=9042, help='Cassandra cluster port'),
    cfg.BoolOpt('ssl_enabled', default=False,
                help='Communicate with Cassandra over SSL?'),
    cfg.StrOpt('ssl_ca_certs', default='',
               help='Absolute path to the appropriate .crt file'),
    cfg.BoolOpt('auth_enabled', default=False,
                help='Does Cassandra have authentication enabled?'),
    cfg.StrOpt('username', default='', help='Cassandra username'),
    cfg.StrOpt('password', default='', help='Cassandra password'),
    cfg.StrOpt('load_balance_strategy', default='RoundRobinPolicy',
               help='Load balancing strategy for connecting to cluster nodes'),
    cfg.StrOpt('consistency_level', default='ONE',
               help='Consistency level of your cassandra query'),
    cfg.StrOpt('migrations_consistency_level', default='LOCAL_QUORUM',
               help='Consistency level of cassandra migration queries'),
    cfg.IntOpt('max_schema_agreement_wait', default=10,
               help='The maximum duration (in seconds) that the driver will'
               ' wait for schema agreement across the cluster.'),
    cfg.StrOpt('keyspace', default='poppy',
               help='Keyspace for all queries made in session'),
    cfg.DictOpt(
        'replication_strategy',
        default={
            'class': 'SimpleStrategy',
            'replication_factor': '1'
        },
        help='Replication strategy for Cassandra cluster'
    ),
    cfg.StrOpt(
        'migrations_path',
        default=os.path.join(os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)))),
            'storage',
            'cassandra',
            'migrations'),
        help='Path to directory containing CQL migration scripts',
    )
]

AKAMAI_CASSANDRA_STORAGE_GROUP = 'drivers:provider:akamai:storage'

LOG = log.getLogger(__name__)


GET_PROVIDER_INFO = '''
    SELECT info from providers_info
    WHERE provider_name = %(provider_name)s
'''

UPDATE_PROVIDER_INFO = '''
    UPDATE providers_info
    set info = %(info)s
    WHERE provider_name = %(provider_name)s
'''

CREATE_PROVIDER_INFO = '''
    INSERT INTO providers_info (
        provider_name,
        info
        )
    VALUES (%(provider_name)s,
        %(info)s)
'''


def _connection(conf, datacenter, keyspace=None):
    """connection.

    :param datacenter
    :returns session
    """
    ssl_options = None
    if conf.ssl_enabled:
        ssl_options = {
            'ca_certs': conf.ssl_ca_certs,
            'ssl_version': ssl.PROTOCOL_TLSv1
        }

    auth_provider = None
    if conf.auth_enabled:
        auth_provider = auth.PlainTextAuthProvider(
            username=conf.username,
            password=conf.password
        )

    load_balancing_policy_class = getattr(policies, conf.load_balance_strategy)
    if load_balancing_policy_class is policies.DCAwareRoundRobinPolicy:
        load_balancing_policy = load_balancing_policy_class(datacenter)
    else:
        load_balancing_policy = load_balancing_policy_class()

    cluster_connection = cluster.Cluster(
        conf.cluster,
        auth_provider=auth_provider,
        load_balancing_policy=load_balancing_policy,
        port=conf.port,
        ssl_options=ssl_options,
        max_schema_agreement_wait=conf.max_schema_agreement_wait
    )

    session = cluster_connection.connect()
    if not keyspace:
        keyspace = conf.keyspace
    try:
        session.set_keyspace(keyspace)
    except cassandra.InvalidRequest:
        _create_keyspace(session, keyspace, conf.replication_strategy)

    migration_session = copy.copy(session)
    migration_session.default_consistency_level = \
        getattr(cassandra.ConsistencyLevel, conf.migrations_consistency_level)
    _run_migrations(keyspace, conf.migrations_path, migration_session)

    session.row_factory = query.dict_factory

    return session


def _create_keyspace(session, keyspace, replication_strategy):
    """create_keyspace.

    :param keyspace
    :param replication_strategy
    """
    LOG.debug('Creating keyspace: ' + keyspace)

    # replication factor will come in as a string with quotes already
    session.execute(
        "CREATE KEYSPACE " + keyspace + " " +
        "WITH REPLICATION = " + str(replication_strategy) + ";"
    )
    session.set_keyspace(keyspace)


def _run_migrations(keyspace, migrations_path, session):
    LOG.debug('Running schema migration(s) on keyspace: %s' % keyspace)

    schema_migrator = migrator.Migrator(migrations_path, session)
    schema_migrator.run_migrations()


class CassandraSanInfoStorage(base.BaseAkamaiSanInfoStorage):

    def __init__(self, conf):
        super(CassandraSanInfoStorage, self).__init__(conf)

        self._conf.register_opts(_DEFAULT_OPTIONS)
        if self._conf.use_same_storage_driver:
            from poppy.storage.cassandra import driver
            self._conf.register_opts(driver.CASSANDRA_OPTIONS,
                                     group=driver.CASSANDRA_GROUP)
            self.cassandra_conf = self._conf[driver.CASSANDRA_GROUP]
        else:
            self._conf.register_opts(CASSANDRA_OPTIONS,
                                     group=AKAMAI_CASSANDRA_STORAGE_GROUP)
            self.cassandra_conf = self._conf[AKAMAI_CASSANDRA_STORAGE_GROUP]
        self.datacenter = conf.datacenter
        self.consistency_level = getattr(
            cassandra.ConsistencyLevel,
            self.cassandra_conf.consistency_level)

    @decorators.lazy_property(write=False)
    def connection(self):
        return _connection(self.cassandra_conf, self.datacenter)

    @property
    def session(self):
        return self.connection

    def _get_akamai_provider_info(self):
        args = {
            "provider_name": 'akamai'
        }

        stmt = query.SimpleStatement(
            GET_PROVIDER_INFO,
            consistency_level=self.consistency_level)
        results = self.session.execute(stmt, args)
        complete_results = list(results)
        if len(complete_results) != 1:
            raise ValueError('No akamai providers info found.')

        result = complete_results[0]

        return result

    def _get_akamai_san_certs_info(self):
        return json.loads(self._get_akamai_provider_info()['info']['san_info'])

    def list_all_san_cert_names(self):
        return self._get_akamai_san_certs_info().keys()

    def get_cert_info(self, san_cert_name):
        the_san_cert_info = self._get_akamai_san_certs_info().get(
            san_cert_name
        )

        if the_san_cert_info is None:
            raise ValueError('No san cert info found for %s.' % san_cert_name)

        jobId = the_san_cert_info.get("jobId")
        issuer = the_san_cert_info.get("issuer")
        ipVersion = the_san_cert_info.get("ipVersion")
        slot_deployment_klass = the_san_cert_info.get("slot_deployment_klass")

        res = {
            # This will always be the san cert name
            'cnameHostname': san_cert_name,
            'jobId': jobId,
            'issuer': issuer,
            'createType': 'modSan',
            'ipVersion': ipVersion,
            'slot-deployment.class': slot_deployment_klass,
            'product': 'ion_premier'
        }

        if any([i for i in [jobId, issuer, ipVersion, slot_deployment_klass]
                if i is None]):
            raise ValueError("San info error: %s" % res)

        return res

    def get_cert_config(self, san_cert_name):
        res = self.get_cert_info(san_cert_name)
        res['spsId'] = self.get_cert_last_spsid(san_cert_name)
        return res

    def save_cert_last_spsid(self, san_cert_name, sps_id_value):
        san_info = self._get_akamai_san_certs_info()
        the_san_cert_info = san_info.get(
            san_cert_name
        )

        if the_san_cert_info is None:
            raise ValueError('No san cert info found for %s.' % san_cert_name)

        the_san_cert_info['spsId'] = sps_id_value
        san_info[san_cert_name] = the_san_cert_info
        # Change the previous san info in the overall provider_info dictionary
        provider_info = dict(self._get_akamai_provider_info()['info'])
        provider_info['san_info'] = json.dumps(san_info)

        stmt = query.SimpleStatement(
            UPDATE_PROVIDER_INFO,
            consistency_level=self.consistency_level)

        args = {
            'provider_name': 'akamai',
            'info': provider_info
        }

        self.session.execute(stmt, args)

    def get_cert_last_spsid(self, san_cert_name):
        the_san_cert_info = self._get_akamai_san_certs_info().get(
            san_cert_name
        )

        if the_san_cert_info is None:
            raise ValueError('No san cert info found for %s.' % san_cert_name)

        spsId = the_san_cert_info.get('spsId')
        return spsId

    def update_san_info(self, san_info_dict):
        provider_info = {}
        provider_info['san_info'] = json.dumps(san_info_dict)

        stmt = query.SimpleStatement(
            CREATE_PROVIDER_INFO,
            consistency_level=self.consistency_level)

        args = {
            'provider_name': 'akamai',
            'info': provider_info
        }

        self.session.execute(stmt, args)
