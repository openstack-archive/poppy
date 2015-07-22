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

"""Mail Notification Driver implementation."""

from oslo_config import cfg

from poppy.notification import base
from poppy.notification.mail import controller


class MailNotificationDriver(base.Driver):
    """Mail Notification Driver."""

    def __init__(self, conf):
        super(MailNotificationDriver, self).__init__(conf)

    @property
    def services_controller(self):
        """Hook for service controller.

        :return service_controller
        """

        return controller.ServicesController(self)

    @property
    def is_alive(self):
        return True

    @property
    def client(self):
        raise None
