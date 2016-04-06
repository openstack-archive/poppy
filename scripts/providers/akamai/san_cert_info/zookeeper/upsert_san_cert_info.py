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

from poppy.provider.akamai.cert_info_storage import zookeeper_storage
from poppy.provider.akamai import driver


CONF = cfg.CONF
CONF.register_cli_opts(zookeeper_storage.AKAMAI_OPTIONS,
                       group=zookeeper_storage.AKAMAI_GROUP)
CONF.register_cli_opt(
    cfg.ListOpt('san_cert_cnames',
                help='A list of san certs cnamehost names'),
    group=driver.AKAMAI_GROUP)
CONF(prog='akamai-config')


def main():
    zk_storage = zookeeper_storage.ZookeeperSanInfoStorage(CONF)

    san_attribute_default_list = {
        'issuer': 'symentec',
        'ipVersion': 'ipv4',
        'slot_deployment_klass': 'esslType',
        'jobId': None}
    for san_cert_name in CONF[driver.AKAMAI_GROUP].san_cert_cnames:
        print("Upsert SAN info for :%s" % (san_cert_name))
        for attr in san_attribute_default_list:
            user_input = None
            while ((user_input or "").strip() or user_input) in ["", None]:
                user_input = raw_input('Please input value for attr: %s, '
                                       'San cert: %s,'
                                       'default value: %s'
                                       ' (if default is None, '
                                       'that means a real value has to'
                                       ' be input): ' %
                                       (attr,
                                        san_cert_name,
                                        san_attribute_default_list[attr]))
                if san_attribute_default_list[attr] is None:
                    continue
                else:
                    user_input = san_attribute_default_list[attr]
                    break
            zk_storage._save_cert_property_value(san_cert_name, attr,
                                                 user_input)


if __name__ == "__main__":
    '''example usage:
    python upsert_san_cert_info.py '
    '--drivers:provider:akamai:storage-storage_backend_type zookeeper'
    '--drivers:provider:akamai:storage-storage_backend_host 192.168.59.103'
    '--drivers:provider:akamai-san_cert_cnames'
    secure1.san1.altcdn.com,secure2.san1.altcdn.com'''
    main()
