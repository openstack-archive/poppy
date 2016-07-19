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

from cassandra import query
from oslo_log import log

from poppy.storage import base

LOG = log.getLogger(__name__)

CQL_SET_SETTING = '''
    UPDATE settings set value = %(value)s
    WHERE setting = %(setting)s
'''

CQL_GET_SETTING = '''
    SELECT value FROM settings
    WHERE setting = %(setting)s
'''


class SettingsController(base.SettingsController):

    """Settings Controller."""

    @property
    def session(self):
        """Get session.

        :returns session
        """
        return self._driver.database

    def get_san_cert_hostname_limit(self):
        """Get the san cert hostname limit setting.

        :returns limit, if limit exists else None.
        """
        max_services = self._driver.max_services_conf.max_services_per_project

        try:
            LOG.info("Checking if non-default san cert hostname limit exists.")

            args = {
                'setting': 'san_cert_hostname_limit',
            }

            stmt = query.SimpleStatement(
                CQL_GET_SETTING,
                consistency_level=self._driver.consistency_level
            )
            result_set = self.session.execute(stmt, args)
            complete_results = list(result_set)
            if complete_results:
                LOG.info(
                    "Checking for san_cert_hostname_limit "
                    "existence yielded {0}".format(str(complete_results))
                )

                result = complete_results[0]

                san_cert_hostname_limit = result.get('value')
                return san_cert_hostname_limit
            else:
                LOG.info(
                    "Checking for san_cert_hostname_limit "
                    "did not yield results, therefore defaulting "
                    "to {0}".format(max_services)
                )
                return max_services

        except ValueError as ex:
            LOG.warning(
                "Query for san_cert_hostname_limit exists failed! {0}".format(
                    ex
                )
            )
            return None

    def set_san_cert_hostname_limit(self, limit):

        LOG.info("Updating san_cert_hostname_limit to {0}.".format(limit))
        args = {
            'setting': 'san_cert_hostname_limit',
            'value': limit,
        }
        stmt = query.SimpleStatement(
            CQL_SET_SETTING,
            consistency_level=self._driver.consistency_level
        )

        self.session.execute(stmt, args)

        LOG.info("san_cert_hostname_limit set to {0}.".format(limit))
