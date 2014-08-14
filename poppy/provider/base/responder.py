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

    def created(self, domain):
        return {
            self.provider: {
                "domain": domain
            }
        }

    def updated(self, domain):
        return {
            self.provider: {
                "domain": domain
            }
        }

    def deleted(self, domain):
        return {
            self.provider: {
                "domain": domain
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
