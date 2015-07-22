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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class NotificationDriverBase(object):
    """Interface definition for notification drivers.

    :param conf: Configuration containing options for this driver.
    :type conf: `oslo_config.ConfigOpts`
    """

    def __init__(self, conf):
        self._conf = conf

    @abc.abstractproperty
    def services_controller(self):
        """Returns the driver's hostname controller.

         :raises NotImplementedError
        """
        raise NotImplementedError
