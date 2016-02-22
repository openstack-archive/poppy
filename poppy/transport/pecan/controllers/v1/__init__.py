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

"""Pecan v1.0 Controllers"""

from poppy.transport.pecan.controllers.v1 import admin
from poppy.transport.pecan.controllers.v1 import flavors
from poppy.transport.pecan.controllers.v1 import health
from poppy.transport.pecan.controllers.v1 import home
from poppy.transport.pecan.controllers.v1 import ping
from poppy.transport.pecan.controllers.v1 import services
from poppy.transport.pecan.controllers.v1 import ssl_certificates


# Hoist into package namespace
Admin = admin.AdminController
DNSHealth = health.DNSHealthController
Distributed_Task_Health = health.DistributedTaskHealthController
Flavors = flavors.FlavorsController
Health = health.HealthController
Home = home.HomeController
Ping = ping.PingController
ProviderHealth = health.ProviderHealthController
Services = services.ServicesController
SSLCertificate = ssl_certificates.SSLCertificateController
StorageHealth = health.StorageHealthController
