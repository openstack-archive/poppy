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

from oslo_log import log

from poppy.storage import base

LOG = log.getLogger(__name__)

settings_store = {}


class SettingsController(base.SettingsController):

    """Settings Controller."""

    def __init__(self, driver):
        super(SettingsController, self).__init__(driver)

        self.settings_store = settings_store

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
        LOG.info("Checking if non-default san_cert_hostname_limit exists.")

        if 'san_cert_hostname_limit' in self.settings_store:
            LOG.info(
                "Checking for san_cert_hostname_limit "
                "existence yielded {0}".format(
                    self.settings_store['san_cert_hostname_limit']
                )
            )

            san_cert_hostname_limit = self.settings_store.get(
                'san_cert_hostname_limit'
            )
            return san_cert_hostname_limit
        else:
            LOG.info(
                "Checking for san_cert_hostname_limit "
                "did not yield results, therefore defaulting "
                "to {0}.".format(None)
            )
            return None

    def set_san_cert_hostname_limit(self, limit):

        LOG.info("Updating san_cert_hostname_limit to {0}.".format(limit))

        self.settings_store['san_cert_hostname_limit'] = limit

        LOG.info("san_cert_hostname_limit set to {0}.".format(limit))
