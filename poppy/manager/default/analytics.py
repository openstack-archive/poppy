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
import json

from oslo_log import log

from poppy.common import errors
from poppy.manager import base

LOG = log.getLogger(__name__)


class AnalyticsController(base.AnalyticsController):

    def get_metrics_by_domain(self, project_id, domain_name, **extras):
        # TODO(TheSriram): Insert call to metrics driver
        storage_controller = self._driver.storage.services_controller
        result = storage_controller.get_service_details_by_domain_name(
            domain_name=domain_name)
        if not result.provider_details:
            msg = "Provider Details were None " \
                  "for the service_id: {0} " \
                  "corresponding to project_id: {1}".format(result.service_id,
                                                            project_id)
            LOG.warn(msg)
            raise errors.ServiceProviderDetailsNotFound(msg)
        if not result:
            msg = "Domain: {0} was not found for project_id: {1}".format(
                domain_name, project_id)
            LOG.warn(msg)
            raise errors.ServiceNotFound(msg)

        provider_details_dict = result.provider_details

        provider_for_domain = None

        for provider, provider_details in provider_details_dict.items():
            if provider_details.get_domain_access_url(domain=domain_name):
                provider_for_domain = provider

        if not provider_for_domain:
            raise ValueError

        provider_obj = self._driver.providers[provider_for_domain.lower()].obj
        provider_service_controller = provider_obj.service_controller
        extras['metrics_controller'] = self._driver.metrics.services_controller
        metrics = provider_service_controller.get_metrics_by_domain(
            project_id, domain_name, provider_obj.regions, **extras)

        # NOTE(TheSriram): Returning Stubbed return value
        # TODO(TheSriram): return metrics instead of stubbed value
        metrics_response = {
            "domain": "example.com",
            "StatusCodes_2XX": [
                {
                    "US": {
                        "1453136297": 24,
                        "1453049897": 45
                    }
                },
                {
                    "EMEA": {
                        "1453136297": 123,
                        "1453049897": 11
                    }
                }
            ]
        }

        return json.dumps(metrics_response)
