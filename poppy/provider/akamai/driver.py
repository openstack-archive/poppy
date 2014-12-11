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

from akamai import edgegrid
from oslo.config import cfg
import requests

from poppy.provider.akamai import controllers
from poppy.provider import base

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

    # Akama client specific configuration numbers
    cfg.StrOpt(
        'akamai_http_config_number',
        help='Akamai configuration number for http policies'),
    cfg.StrOpt(
        'akamai_https_config_number',
        help='Akamai configuration number for https policies'),
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
        self.https_conf_number = self.akamai_conf.akamai_https_config_number

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

    def is_alive(self):
        return True

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
    def service_controller(self):
        """Returns the driver's hostname controller."""
        return controllers.ServiceController(self)
