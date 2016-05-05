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

"""Mail Notification Driver implementation."""

import re

from oslo_config import cfg

from poppy.notification import base
from poppy.notification.mailgun import controller

MAIL_NOTIFICATION_OPTIONS = [
    cfg.StrOpt('mailgun_api_key',
               help='Mail gun secret API Key'),
    cfg.IntOpt('retry_send', default=5,
               help='Mailgun send retry'),
    cfg.StrOpt('mailgun_request_url',
               help='Mail gun request url'),
    cfg.StrOpt('sand_box',
               help='Mail gun sand box domain'),
    cfg.StrOpt('from_address', default='noreply@poppycdn.org',
               help='Sent from email address'),
    cfg.ListOpt('recipients',
                help='A list of emails addresses to receive notification '),
    cfg.StrOpt('notification_subject',
               default='Poppy SSL Certificate Provisioned/Deleted',
               help='The subject of the email notification ')
]

MAIL_NOTIFICATION_GROUP = 'drivers:notification:mailgun'


def validate_email_address(email_address):
    email_re = re.compile('(\w+[.|\w])*@(\w+[.])*\w+')
    return email_re.match(email_address) is not None


class MailNotificationDriver(base.Driver):
    """Mail Notification Driver."""

    def __init__(self, conf):
        super(MailNotificationDriver, self).__init__(conf)
        conf.register_opts(MAIL_NOTIFICATION_OPTIONS,
                           group=MAIL_NOTIFICATION_GROUP)
        self.mail_notification_conf = conf[MAIL_NOTIFICATION_GROUP]
        self.retry_send = self.mail_notification_conf.retry_send
        self.mailgun_api_key = self.mail_notification_conf.mailgun_api_key
        self.mailgun_request_url = (
            self.mail_notification_conf.mailgun_request_url)
        self.sand_box = self.mail_notification_conf.sand_box
        self.from_address = self.mail_notification_conf.from_address
        self.recipients = self.mail_notification_conf.recipients
        self.notification_subject = (
            self.mail_notification_conf.notification_subject)

        # validate email addresses
        if not validate_email_address(self.from_address):
            raise ValueError(
                "Notification config error: "
                "{0} is not a valid email address".format(self.from_address)
            )

        for address in self.recipients:
            if not validate_email_address(address):
                raise ValueError(
                    "Notification config error: "
                    "{0} is not a valid email address".format(address)
                )

    @property
    def services_controller(self):
        """Hook for service controller.

        :return service_controller
        """

        return controller.ServicesController(self)
