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

from poppy.manager.base import analytics
from poppy.manager.base import background_job
from poppy.manager.base import driver
from poppy.manager.base import flavors
from poppy.manager.base import home
from poppy.manager.base import services
from poppy.manager.base import ssl_certificate


Driver = driver.ManagerDriverBase

AnalyticsController = analytics.AnalyticsController
BackgroundJobController = background_job.BackgroundJobControllerBase
FlavorsController = flavors.FlavorsControllerBase
ServicesController = services.ServicesControllerBase
HomeController = home.HomeControllerBase
SSLCertificateController = ssl_certificate.SSLCertificateController
