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

"""Akamai CDN Provider implementation."""

import json

from akamai import edgegrid
from oslo_config import cfg
import requests

from poppy.openstack.common import log
from poppy.provider.akamai import controllers
from poppy.provider.akamai.mod_san_queue import zookeeper_queue
from poppy.provider.akamai.san_info_storage import zookeeper_storage
from poppy.provider import base

LOG = log.getLogger(__name__)


AKAMAI_OPTIONS = [
    # credentials && base URL for policy API
    cfg.StrOpt(
        'policy_api_client_token',
        help='Akamai client token for policy API'),
    cfg.StrOpt(
        'policy_api_client_secret',
        help='Akamai client secret for policy API'),
    cfg.StrOpt(
        'policy_api_access_token',
        help='Akamai access token for policy API'),
    cfg.StrOpt(
        'policy_api_base_url',
        help='Akamai policy API base URL'),
    # credentials && base URL for CCU API
    # for purging
    cfg.StrOpt(
        'ccu_api_client_token',
        help='Akamai client token for CCU API'),
    cfg.StrOpt(
        'ccu_api_client_secret',
        help='Akamai client secret for CCU API'),
    cfg.StrOpt(
        'ccu_api_access_token',
        help='Akamai access token for CCU API'),
    cfg.StrOpt(
        'ccu_api_base_url',
        help='Akamai CCU Purge API base URL'),
    # Access URL in Akamai chain
    cfg.StrOpt(
        'akamai_access_url_link',
        help='Akamai domain access_url link'),
    cfg.StrOpt(
        'akamai_https_access_url_suffix',
        help='Akamai domain ssl access url suffix'),

    # Akamai client specific configuration numbers
    cfg.StrOpt(
        'akamai_http_config_number',
        help='Akamai configuration number for http policies'),
    cfg.StrOpt(
        'akamai_https_shared_config_number',
        help='Akamai configuration number for shared wildcard https policies'
    ),
    cfg.ListOpt(
        'akamai_https_san_config_numbers',
        help='A list of Akamai configuration number for '
             'SAN cert https policies'
    ),
    cfg.ListOpt(
        'akamai_https_custom_config_numbers',
        help='A list of Akamai configuration number for '
             'Custom cert https policies'
    ),

    # SANCERT related configs
    cfg.ListOpt('san_cert_cnames',
                help='A list of san certs cnamehost names'),
    cfg.IntOpt('san_cert_hostname_limit', default=80,
               help='default limit on how many hostnames can'
               ' be held by a SAN cert'),

    # related info for SPS && PAPI APIs
    cfg.StrOpt(
        'contract_id',
        help='Operator contractID'),
    cfg.StrOpt(
        'group_id',
        help='Operator groupID'),
    cfg.StrOpt(
        'property_id',
        help='Operator propertyID')
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class CDNProvider(base.Driver):

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(AKAMAI_OPTIONS,
                                 group=AKAMAI_GROUP)
        self.akamai_conf = self._conf[AKAMAI_GROUP]
        self.akamai_policy_api_base_url = ''.join([
            str(self.akamai_conf.policy_api_base_url),
            'partner-api/v1/network/production/properties/',
            '{configuration_number}/sub-properties/{policy_name}/policy'
        ])
        self.akamai_ccu_api_base_url = ''.join([
            str(self.akamai_conf.ccu_api_base_url),
            'ccu/v2/queues/default'
        ])

        self.http_conf_number = self.akamai_conf.akamai_http_config_number
        self.https_shared_conf_number = (
            self.akamai_conf.akamai_https_shared_config_number)
        self.https_san_conf_number = (
            self.akamai_conf.akamai_https_san_config_numbers[-1])
        self.https_custom_conf_number = (
            self.akamai_conf.akamai_https_custom_config_numbers[-1])

        self.akamai_access_url_link = self.akamai_conf.akamai_access_url_link
        self.akamai_https_access_url_suffix = (
            self.akamai_conf.akamai_https_access_url_suffix
        )

        self.akamai_policy_api_client = requests.Session()
        self.akamai_policy_api_client.auth = edgegrid.EdgeGridAuth(
            client_token=self.akamai_conf.policy_api_client_token,
            client_secret=self.akamai_conf.policy_api_client_secret,
            access_token=self.akamai_conf.policy_api_access_token
        )

        self.akamai_ccu_api_client = requests.Session()
        self.akamai_ccu_api_client.auth = edgegrid.EdgeGridAuth(
            client_token=self.akamai_conf.ccu_api_client_token,
            client_secret=self.akamai_conf.ccu_api_client_secret,
            access_token=self.akamai_conf.ccu_api_access_token
        )

        self.akamai_sps_api_base_url = ''.join([
            str(self.akamai_conf.policy_api_base_url),
            'config-secure-provisioning-service/v1'
            '/sps-requests/{spsId}?contractId=%s&groupId=%s' % (
                self.akamai_conf.contract_id,
                self.akamai_conf.group_id
            )
        ])

        self.san_cert_cnames = self.akamai_conf.san_cert_cnames
        self.san_cert_hostname_limit = self.akamai_conf.san_cert_hostname_limit

        self.akamai_sps_api_client = self.akamai_policy_api_client

        self.san_info_storage = (
            zookeeper_storage.ZookeeperSanInfoStorage(self._conf))
        self.mod_san_queue = (
            zookeeper_queue.ZookeeperModSanQueue(self._conf))

    def is_alive(self):

        request_headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }

        resp = self.policy_api_client.put(
            self.akamai_policy_api_base_url.format(
                configuration_number=self.http_conf_number,
                policy_name='healthcheck'),
            data=json.dumps({'rules': []}),
            headers=request_headers)

        if resp.ok:
            return True
        else:
            LOG.warn("Akamai Health Check Failed")
            LOG.warn("Response Status Code : {0}".format(resp.status_code))
            LOG.warn("Response Text : {0}".format(resp.text))
            return False

    @property
    def provider_name(self):
        return "Akamai"

    @property
    def policy_api_client(self):
        return self.akamai_policy_api_client

    @property
    def ccu_api_client(self):
        return self.akamai_ccu_api_client

    @property
    def sps_api_client(self):
        return self.akamai_sps_api_client

    @property
    def papi_api_client(self):
        return self.akamai_papi_api_client

    @property
    def service_controller(self):
        """Returns the driver's hostname controller."""
        return controllers.ServiceController(self)
