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

import traceback


class Responder(object):
    """Responder Class."""

    def __init__(self, dns_name):
        self.dns = dns_name

    def failed(self, msg):
        """failed.

        :param msg
        :returns {error, error details}
        """

        return {
            'error': msg,
            'error_detail': traceback.format_exc()
        }

    def created(self, dns_details):
        """created.

        :param dns_details
        :returns dns_details
        """

        return dns_details

    def updated(self, dns_details):
        """updated.

        :param dns_details
        :returns dns_details
        """

        return dns_details

    def deleted(self, dns_details):
        """deleted.

        :param dns_details
        :returns dns_details
        """

        return dns_details
