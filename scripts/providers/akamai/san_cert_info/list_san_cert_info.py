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

from poppy.provider.akamai.san_info_storage import zookeeper_storage


AKAMAI_OPTIONS = [
    # storage backend configs for long running tasks
    cfg.StrOpt(
        'storage_backend_type',
        help='SAN Cert info storage backend'),
    cfg.ListOpt('storage_backend_host', default=['localhost'],
                help='default san info storage backend server hosts'),
    cfg.IntOpt('storage_backend_port', default=2181, help='default'
               ' default san info storage backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'san_info_storage_path', default='/san_info', help='zookeeper backend'
        ' path for san cert info'),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


def main():

    my_conf = cfg.ConfigOpts()
    zk_storage = zookeeper_storage.ZookeeperSanInfoStorage(my_conf)

    all_san_cert_names = zk_storage.list_all_san_cert_names()
    for san_cert_name in all_san_cert_names:
        print("%s:%s" % (san_cert_name,
                         str(zk_storage.get_cert_info(san_cert_name))))

if __name__ == "__main__":
    main()
