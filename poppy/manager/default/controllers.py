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

from poppy.manager.default import analytics
from poppy.manager.default import background_job
from poppy.manager.default import flavors
from poppy.manager.default import health
from poppy.manager.default import home
from poppy.manager.default import services
from poppy.manager.default import ssl_certificate


Analytics = analytics.AnalyticsController
BackgroundJob = background_job.BackgroundJobController
Home = home.DefaultHomeController
Flavors = flavors.DefaultFlavorsController
Health = health.DefaultHealthController
Services = services.DefaultServicesController
SSLCertificate = ssl_certificate.DefaultSSLCertificateController
