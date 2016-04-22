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

from oslo_config import cfg

from poppy.provider.akamai.cert_info_storage import base
from poppy.provider.akamai import utils


AKAMAI_OPTIONS = [
    # storage backend configs for long running tasks
    cfg.StrOpt(
        'storage_backend_type',
        default='zookeeper',
        help='SAN Cert info storage backend'),
    cfg.ListOpt('storage_backend_host', default=['localhost'],
                help='default san info storage backend server hosts'),
    cfg.IntOpt('storage_backend_port', default=2181, help='default'
               ' default san info storage backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'cert_info_storage_path',
        default='/cert_info',
        help='zookeeper backend'
        ' path for san cert info'
    ),
]

AKAMAI_GROUP = 'drivers:provider:akamai:storage'


class ZookeeperSanInfoStorage(base.BaseAkamaiSanInfoStorage):

    def __init__(self, conf):
        super(ZookeeperSanInfoStorage, self).__init__(conf)

        self._conf.register_opts(AKAMAI_OPTIONS,
                                 group=AKAMAI_GROUP)
        self.akamai_conf = self._conf[AKAMAI_GROUP]
        self.cert_info_storage_path = self.akamai_conf.cert_info_storage_path

        self.zookeeper_client = utils.connect_to_zookeeper_storage_backend(
            self.akamai_conf)

    def _zk_path(self, san_cert_name, property_name=None):
        path_names_list = [self.cert_info_storage_path, san_cert_name,
                           property_name] if property_name else (
            [self.cert_info_storage_path, san_cert_name])
        return '/'.join(path_names_list)

    def list_all_san_cert_names(self):
        self.zookeeper_client.ensure_path(self.cert_info_storage_path)
        return self.zookeeper_client.get_children(self.cert_info_storage_path)

    def get_cert_info(self, san_cert_name):
        self.zookeeper_client.ensure_path(self._zk_path(san_cert_name, None))
        jobId, _ = self.zookeeper_client.get(self._zk_path(san_cert_name,
                                             "jobId"))
        issuer, _ = self.zookeeper_client.get(self._zk_path(san_cert_name,
                                              "issuer"))
        ipVersion, _ = self.zookeeper_client.get(
            self._zk_path(san_cert_name, "ipVersion"))
        slot_deployment_klass, _ = self.zookeeper_client.get(
            self._zk_path(san_cert_name, "slot_deployment_klass"))
        return {
            # This will always be the san cert name
            'cnameHostname': san_cert_name,
            'jobId': jobId,
            'issuer': issuer,
            'createType': 'modSan',
            'ipVersion': ipVersion,
            'slot-deployment.class': slot_deployment_klass,
            'product': 'ion_premier'
        }

    def save_cert_last_ids(self, san_cert_name,
                           sps_id_value, job_id_value=None):
        self._save_cert_property_value(san_cert_name,
                                       'spsId', sps_id_value)
        if job_id_value is not None:
            self._save_cert_property_value(
                san_cert_name, 'jobId', job_id_value)

    def get_cert_last_spsid(self, san_cert_name):
        my_sps_id_path = self._zk_path(san_cert_name, 'spsId')
        self.zookeeper_client.ensure_path(my_sps_id_path)
        spsId, _ = self.zookeeper_client.get(my_sps_id_path)
        return spsId

    def _save_cert_property_value(self, san_cert_name,
                                  property_name, value):
        property_name_path = self._zk_path(san_cert_name, property_name)
        self.zookeeper_client.ensure_path(property_name_path)
        self.zookeeper_client.set(property_name_path, str(value))
