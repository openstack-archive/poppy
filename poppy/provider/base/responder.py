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

import traceback

from poppy.openstack.common import log

LOG = log.getLogger(__name__)


class Responder(object):
    """Responder Class."""

    def __init__(self, provider_type):
        self.provider = provider_type

    def failed(self, msg):
        """failed.

        :param msg
        :returns provider msg{msg, error details}
        """

        # Add this log information for easing debug
        LOG.info(
            'Error happened during provider operation. message: %(message)s,'
            'error_detail: %(error_detail)s',
            {'message': msg,
             'error_detail': traceback.format_exc()
             }
        )

        return {
            self.provider: {
                'error': msg,
                'error_detail': traceback.format_exc(),
            }
        }

    def created(self, provider_service_id, links, **extras):
        """failed.

        :param provider_service_id
        :param links
        :param **extras
        :returns provider msg{id, links}
        """
        provider_response = {
            'id': provider_service_id,
            'links': links
        }
        provider_response.update(extras)
        return {
            self.provider: provider_response
        }

    def updated(self, provider_service_id, links):
        """updated.

        :param provider_service_id
        :returns provider msg{provider service id}
        """
        provider_response = {
            "id": provider_service_id,
            "links": links
        }

        return {
            self.provider: provider_response
        }

    def deleted(self, provider_service_id):
        """deleted.

        :param provider_service_id
        :returns provider msg{provider service id}
        """
        return {
            self.provider: {
                'id': provider_service_id
            }
        }

    def purged(self, provider_service_id, purge_urls):
        """purged.

        :param provider_service_id
        :param purge_urls
        :returns provider msg{provider service id, purge urls}
        """
        provider_response = {
            'id': provider_service_id,
            'purge_urls': purge_urls
        }
        return {
            self.provider: provider_response
        }

    def get(self, domain_list, origin_list, cache_list):
        """get.

        :param domain_list
        :param origin_list
        :param cache_list
        :returns provider msg{domain, origins, caching}
        """
        return {
            self.provider: {
                'domains': domain_list,
                'origins': origin_list,
                'caching': cache_list
            }
        }
