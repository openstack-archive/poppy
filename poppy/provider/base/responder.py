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

from __future__ import print_function

import sys
import traceback


class Responder(object):
    def __init__(self, provider_type):
        self.provider = provider_type

    def failed(self, msg):
        ex_type, ex, tb = sys.exc_info()

        print("error: {0} {1} {2} {3}".format(self.provider, msg, ex_type, ex))
        traceback.print_tb(tb)

        return {
            self.provider: {
                "error": msg
            }
        }

    def created(self, provider_service_id, links, **extras):
        provider_response = {
            "id": provider_service_id,
            "links": links
        }
        provider_response.update(extras)
        return {
            self.provider: provider_response
        }

    def updated(self, provider_service_id):
        # TODO(tonytan4ever): May need to add link information as return
        return {
            self.provider: {
                "id": provider_service_id
            }
        }

    def deleted(self, provider_service_id):
        return {
            self.provider: {
                "id": provider_service_id
            }
        }

    def get(self, domain_list, origin_list, cache_list):
        return {
            self.provider: {
                "domains": domain_list,
                "origins": origin_list,
                "caching": cache_list
            }
        }
