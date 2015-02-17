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

from poppy.model.helpers import provider_details


def load_from_json(json_data):
    access_urls = json_data.get("access_urls")
    error_info = json_data.get("error_info", )
    provider_service_id = json_data.get("id")
    status = json_data.get("status")
    return provider_details.ProviderDetail(
        provider_service_id=provider_service_id,
        access_urls=access_urls,
        status=status,
        error_info=error_info)
