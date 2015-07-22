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

import requests

from poppy.notification import base
from poppy.openstack.common import log

LOG = log.getLogger(__name__)


class ServicesController(base.ServicesBase):

    """Services Controller Base class."""

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.mailgun_api_key = self.driver.mailgun_api_key
        self.mailgun_request_url = self.driver.mailgun_request_url
        self.sand_box = self.driver.sand_box
        self.from_address = self.driver.from_address
        self.recipients = self.driver.recipients

    def send(self, subject, mail_content):
        """send notification to a (list) of recipients.

        :param subject
        :param mail_content
        :raises NotImplementedError
        """
        res = self._send_mail_notification_via_mailgun(subject, mail_content)
        if res:
            LOG.info("Send email notification successful."
                     "Subject: %s"
                     "Content: %s" % (subject,
                                      mail_content))

        return

    def _send_mail_notification_via_mailgun(self, subject, mail_content):
        '''Send a mail via mail gun'''

        request_url = self.mailgun_request_url.format(self.sand_box)
        response = requests.post(
            request_url,
            auth=('api', self.mailgun_api_key),
            data={
                'from': self.from_address,
                'to': self.recipients,
                'subject': subject,
                'text': mail_content
            }
        )

        if response.status_code != 200:
            LOG.warning("Send email notification failed. Details:"
                        "From: %s"
                        "To: %s"
                        "Subject: %s"
                        "Content: %s" % (self.from_address,
                                         self.recipients,
                                         subject,
                                         mail_content))
            return False
        else:
            return True
