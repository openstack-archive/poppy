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

from oslo_log import log
import requests

from poppy.notification import base

LOG = log.getLogger(__name__)


class ServicesController(base.ServicesBase):

    """Services Controller Base class."""

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.mailgun_api_key = self.driver.mailgun_api_key
        self.retry_send = self.driver.retry_send
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
        """Send a mail via mail gun"""

        request_url = self.mailgun_request_url.format(self.sand_box)
        response_status = False
        attempt = 1

        while not response_status and attempt <= self.retry_send:
            LOG.info("Sending email notification attempt: %s" % str(attempt))
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
            response_status = response.ok
            response_status_code = response.status_code
            response_text = response.text
            LOG.info(
                "Email attempt {0}, status code: {1}, response.ok: {2}".format(
                    attempt, response_status_code, response_status
                )
            )
            LOG.info("Email attempt {0} "
                     "response text: {1}".format(attempt, response_text))
            attempt += 1

        if not response_status:
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
