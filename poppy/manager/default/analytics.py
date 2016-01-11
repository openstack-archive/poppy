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

from poppy.manager import base


class AnalyticsController(base.AnalyticsController):

    def get_metrics_by_domain(self, project_id, domain_name, **extras):
        # TODO(TheSriram): Insert call to metrics driver
        self.metrics_controller = self._driver.metrics.services_controller
        # NOTE(TheSriram): Returning Stubbed return value
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
