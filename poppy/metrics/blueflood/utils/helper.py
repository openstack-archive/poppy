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

import datetime
import time

try:  # pragma: no cover
    import six.moves.urllib.parse as parse
except ImportError:  # pragma: no cover
    import urllib.parse as parse

def set_qs_on_url(url, **params):

    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = parse.urlencode(query)

    return parse.urlunparse(url_parts)

def join_url(base_url, url):
    return parse.urljoin(base_url, url)

def datetime_to_epoch(datetimeobj):
    return time.mktime(datetime.datetime.now().timetuple()) * 1000
