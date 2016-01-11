# Copyright (c) 2016 Rackspace, Inc.
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

import logging

from oslo_config import cfg

from poppy.cache import base
from poppy.cache.cloud_metrics import controllers


LOG = logging.getLogger(__name__)

CLOUD_METRICS_OPTIONS = [
    cfg.StrOpt('cloud_metrics_url', default='https://www.metrics.com',
               help='Metrics url for retrieving cached content'),
]

CLOUD_METRICS_GROUP = 'drivers:cache:cloud_metrics'


class CloudMetricsCacheDriver(base.Driver):
    """Cloud Metrics cache Driver."""

    def __init__(self, conf):
        super(CloudMetricsCacheDriver, self).__init__(conf)
        conf.register_opts(CLOUD_METRICS_OPTIONS, group=CLOUD_METRICS_GROUP)
        self.cache_conf = conf[CLOUD_METRICS_GROUP]

    def is_alive(self):
        """Health check for Cloud Metrics driver."""
        return True

    @property
    def vendor_name(self):
        """cache name.

        :returns 'Cloud Metrics'
        """
        return 'Cloud Metrics'

    @property
    def services_controller(self):
        """services_controller.

        :returns service controller
        """
        return controllers.ServicesController(self)
