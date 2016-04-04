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
from six.moves import input

from poppy.provider.akamai.cert_info_storage import cassandra_storage
from poppy.provider.akamai import driver


CONF = cfg.CONF
CONF.register_cli_opts(cassandra_storage.CASSANDRA_OPTIONS,
                       group=cassandra_storage.AKAMAI_CASSANDRA_STORAGE_GROUP)
CONF.register_cli_opts(driver.AKAMAI_OPTIONS, driver.AKAMAI_GROUP)
CONF(prog='akamai-config')


def main():
    v_cassandra_storage = cassandra_storage.CassandraSanInfoStorage(CONF)

    sni_attribute_default_list = {
        'enrollmentId': None,
    }

    sni_info_dict = dict()

    for sni_cert_name in CONF[driver.AKAMAI_GROUP].sni_cert_cnames:
        sni_info_dict[sni_cert_name] = {}
        print("Insert SNI info for: {0}".format(sni_cert_name))
        for attr in sni_attribute_default_list:
            user_input = None
            while ((user_input or "").strip() or user_input) in ["", None]:
                user_input = input(
                    'Please input value for attr: {0}, SNI cert: {1}, '
                    'default value: {2} (if default is None, '
                    'that means a real value has to be input): '.format(
                        attr,
                        sni_cert_name,
                        sni_attribute_default_list[attr]
                    )
                )
                # enrollmentId is required
                if user_input in ["", None] and attr == "enrollmentId":
                    break
                if sni_attribute_default_list[attr] is None:
                    continue
                else:
                    user_input = sni_attribute_default_list[attr]
                    break
            sni_info_dict[sni_cert_name][attr] = user_input

    v_cassandra_storage.update_san_info(sni_info_dict, info_type='sni')


if __name__ == "__main__":
    '''
    example usage:
    python upsert_sni_cert_info.py --config-file ~/.poppy/poppy.conf
    '''
    main()
