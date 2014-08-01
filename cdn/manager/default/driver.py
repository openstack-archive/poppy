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

"""Default manager driver implementation."""

from cdn.common import decorators
from cdn.manager import base
from cdn.manager.default import controllers


class DefaultManagerDriver(base.Driver):

    def __init__(self, conf, storage, providers):
        super(DefaultManagerDriver, self).__init__(conf, storage, providers)

    @decorators.lazy_property(write=False)
    def services_controller(self):
        return controllers.Services(self)

    @decorators.lazy_property(write=False)
    def v1_controller(self):
        return controllers.V1(self)
