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

"""CloudFront CDN Provider implementation."""

import boto
from oslo.config import cfg

from poppy.openstack.common import log as logging
from poppy.provider import base
from poppy.provider.cloudfront import controllers


LOG = logging.getLogger(__name__)

CLOUDFRONT_OPTIONS = [
    cfg.StrOpt('aws_access_key_id', help='CloudFront Access Key ID'),
    cfg.StrOpt('aws_secret_access_key', help='CloudFront Secret Acces Key'),
]

CLOUDFRONT_GROUP = 'drivers:provider:cloudfront'


class CDNProvider(base.Driver):

    def __init__(self, conf):
        super(CDNProvider, self).__init__(conf)

        self._conf.register_opts(CLOUDFRONT_OPTIONS, group=CLOUDFRONT_GROUP)
        self.cloudfront_conf = self._conf[CLOUDFRONT_GROUP]
        self.cloudfront_client = boto.connect_cloudfront(
            aws_access_key_id=self.cloudfront_conf.aws_access_key_id,
            aws_secret_access_key=self.cloudfront_conf.aws_secret_access_key)

    def is_alive(self):
        return True

    @property
    def provider_name(self):
        return 'CloudFront'

    def client(self):
        return self.cloudfront_client

    @property
    def service_controller(self):
        return controllers.ServiceController(self)
