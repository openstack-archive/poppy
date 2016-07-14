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

"""Unittests for mail notification driver implementation."""

import mock

from oslo_config import cfg

from poppy.notification.mailgun import driver
from tests.unit import base

MAIL_NOTIFICATION_OPTIONS = [
    cfg.StrOpt('mailgun_api_key', default='123',
               help='Mail gun secret API Key'),
    cfg.IntOpt('retry_send', default=5,
               help='Mailgun send retry'),
    cfg.StrOpt('mailgun_request_url', default='http://123.com/{0}',
               help='Mail gun request url'),
    cfg.StrOpt('sand_box', default='123.com',
               help='Mail gun sand box domain'),
    cfg.StrOpt('from_address', default='noreply@poppycdn.org',
               help='Sent from email address'),
    cfg.ListOpt('recipients', default=['recipient@gmail.com'],
                help='A list of emails addresses to receive notification '),
    cfg.StrOpt('notification_subject',
               default='Poppy SSL Certificate Provisioned',
               help='The subject of the email notification ')
]

MAIL_NOTIFICATION_GROUP = 'drivers:notification:mailgun'


class TestDriver(base.TestCase):

    @mock.patch.object(driver, 'MAIL_NOTIFICATION_OPTIONS',
                       new=MAIL_NOTIFICATION_OPTIONS)
    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.mailgun_notification_driver = (
            driver.MailNotificationDriver(self.conf))

    def test_init(self):
        self.assertTrue(self.mailgun_notification_driver is not None)

    def test_service_controller(self):
        self.assertTrue(self.mailgun_notification_driver.services_controller
                        is not None)
        self.assertTrue(self.mailgun_notification_driver.retry_send == 5)


class TestDriverInit(base.TestCase):

    def setUp(self):
        super(TestDriverInit, self).setUp()

    def test_invalid_from_address(self):
        notification_options = [
            cfg.StrOpt('mailgun_api_key', default='123'),
            cfg.IntOpt('retry_send', default=5),
            cfg.StrOpt('mailgun_request_url', default='http://123.com/{0}'),
            cfg.StrOpt('sand_box', default='123.com'),
            cfg.StrOpt('from_address', default='invalid.email.address'),
            cfg.ListOpt('recipients', default=['recipient@gmail.com']),
            cfg.StrOpt('notification_subject',
                       default='Poppy SSL Certificate Provisioned')
        ]

        with mock.patch.object(
                driver, 'MAIL_NOTIFICATION_OPTIONS', new=notification_options):

            self.conf = cfg.ConfigOpts()

            self.assertRaises(
                ValueError,
                driver.MailNotificationDriver,
                self.conf
            )

    def test_invalid_recipients(self):
        notification_options = [
            cfg.StrOpt('mailgun_api_key', default='123'),
            cfg.IntOpt('retry_send', default=5),
            cfg.StrOpt('mailgun_request_url', default='http://123.com/{0}'),
            cfg.StrOpt('sand_box', default='123.com'),
            cfg.StrOpt('from_address', default='noreply@poppycdn.org'),
            cfg.ListOpt('recipients', default=['invalid.email.address']),
            cfg.StrOpt('notification_subject',
                       default='Poppy SSL Certificate Provisioned')
        ]

        with mock.patch.object(
                driver, 'MAIL_NOTIFICATION_OPTIONS', new=notification_options):

            self.conf = cfg.ConfigOpts()

            self.assertRaises(
                ValueError,
                driver.MailNotificationDriver,
                self.conf
            )
