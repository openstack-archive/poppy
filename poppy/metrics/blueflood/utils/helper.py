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

import calendar
import time

try:  # pragma: no cover
    import six.moves.urllib.parse as parse
except ImportError:  # pragma: no cover
    import urllib.parse as parse

from oslo_log import log

LOG = log.getLogger(__name__)


def set_qs_on_url(url, **params):

    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = parse.urlencode(query)

    return parse.urlunparse(url_parts)


def retrieve_last_relative_url(url):
    url_parts = list(parse.urlparse(url))
    return url_parts[2].split('/')[-1:][0]


def join_url(base_url, url):
    return parse.urljoin(base_url, url)


def datetime_to_epoch(datetime_obj):
    return calendar.timegm(datetime_obj.timetuple()) * 1000


def datetime_from_epoch(ms):
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(ms / 1000))


def resolution_converter_seconds_to_enum(resolution_seconds):

    resolution_resolver = {
        '0': 'FULL',
        '300': 'MIN5',
        '1200': 'MIN20',
        '3600': 'MIN60',
        '14400': 'MIN240',
        '86400': 'MIN1440'
    }
    try:
        return resolution_resolver[resolution_seconds]
    except KeyError:
        msg = 'Resolution of {0} does not translate ' \
              'into BlueFlood time windows, ' \
              'acceptable windows: {1}'.format(resolution_seconds,
                                               resolution_resolver.keys())
        LOG.error(msg)
        raise ValueError(msg)
