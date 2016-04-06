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

from poppy.provider.akamai.cert_info_storage import cassandra_storage
from poppy.provider.akamai import driver


CONF = cfg.CONF
CONF.register_cli_opts(cassandra_storage.CASSANDRA_OPTIONS,
                       group=cassandra_storage.AKAMAI_CASSANDRA_STORAGE_GROUP)
CONF.register_cli_opts(driver.AKAMAI_OPTIONS, driver.AKAMAI_GROUP)
CONF(prog='akamai-config')


def main():
    v_cassandra_storage = cassandra_storage.CassandraSanInfoStorage(CONF)

    san_attribute_default_list = {
        'issuer': 'symantec',
        'ipVersion': 'ipv4',
        'slot_deployment_klass': 'esslType',
        'spsId': None,
        'jobId': None}

    san_info_dict = {
    }
    for san_cert_name in CONF[driver.AKAMAI_GROUP].san_cert_cnames:
        san_info_dict[san_cert_name] = {}
        print("Insert SAN info for :%s" % (san_cert_name))
        for attr in san_attribute_default_list:
            user_input = None
            while ((user_input or "").strip() or user_input) in ["", None]:
                user_input = raw_input('Please input value for attr: %s, '
                                       'San cert: %s,'
                                       'default value: %s'
                                       ' (if default is None, '
                                       'that means a real value has to'
                                       ' be input, except spsId): ' %
                                       (attr,
                                        san_cert_name,
                                        san_attribute_default_list[attr]))
                # We allow not inputing spsId, however if it is in
                # transitioning from the old manual SAN process we NEED
                # to put in spsId
                if user_input in ["", None] and attr == "spsId":
                    break
                if san_attribute_default_list[attr] is None:
                    continue
                else:
                    user_input = san_attribute_default_list[attr]
                    break
            san_info_dict[san_cert_name][attr] = user_input

    v_cassandra_storage.update_san_info(san_info_dict)


if __name__ == "__main__":
    '''
    example usage:
    python upsert_san_cert_info.py --config-file ~/.poppy/poppy.conf
    '''
    main()
