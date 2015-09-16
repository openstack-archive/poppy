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

"""Unittests for TaskFlow distributed_task service_controller."""

import mock
import requests

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

MAIL_NOTIFICATION_GROUP = 'drivers:notification:mail'


class TestServiceController(base.TestCase):

    @mock.patch.object(driver, 'MAIL_NOTIFICATION_OPTIONS',
                       new=MAIL_NOTIFICATION_OPTIONS)
    def setUp(self):
        super(TestServiceController, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.mail_notification_driver = (
            driver.MailNotificationDriver(self.conf))
        self.controller = self.mail_notification_driver.services_controller

    @mock.patch.object(requests, 'post', new=mock.Mock())
    def test_send_mail_notification(self):
        self.assertTrue(self.controller.retry_send == 5)
        self.controller.send("A Subject", "Some random text")
        requests.post.assert_called_once()
