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


CONF = cfg.CONF
CONF.register_cli_opts(zookeeper_storage.AKAMAI_OPTIONS,
                       group=zookeeper_storage.AKAMAI_GROUP)
CONF(prog='akamai-config')


def main():
    zk_storage = zookeeper_storage.ZookeeperSanInfoStorage(CONF)

    all_san_cert_names = zk_storage.list_all_san_cert_names()

    if not all_san_cert_names:
        print ("Currently no SAN cert info has been intialized")

    for san_cert_name in all_san_cert_names:
        print("%s:%s" % (san_cert_name,
                         str(zk_storage.get_cert_info(san_cert_name))))

if __name__ == "__main__":
    """
    example usage:
    python san_cert_info/list_san_cert_info.py
    --drivers:provider:akamai:storage-storage_backend_type zookeeper
    --drivers:provider:akamai:storage-storage_backend_host 192.168.59.103
    """
    main()
